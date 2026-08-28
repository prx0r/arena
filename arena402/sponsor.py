from __future__ import annotations

from dataclasses import asdict
import math
from typing import Iterable

from .mechanism import CampaignState, MechanismConfig, ProviderCampaign, wilson_interval


class CampaignBook:
    def __init__(self, cfg: MechanismConfig | None = None):
        self.cfg = cfg or MechanismConfig()
        self.campaigns: dict[str, ProviderCampaign] = {}
        self.by_provider: dict[str, str] = {}

    def open(self, campaign: ProviderCampaign) -> ProviderCampaign:
        if campaign.provider_id in self.by_provider:
            raise ValueError("provider already has active campaign")
        if campaign.funded_usd <= 0 or campaign.remaining_usd < 0:
            raise ValueError("funding")
        self.campaigns[campaign.campaign_id] = campaign
        self.by_provider[campaign.provider_id] = campaign.campaign_id
        return campaign

    def get_provider(self, provider_id: str) -> ProviderCampaign | None:
        cid = self.by_provider.get(provider_id)
        return None if cid is None else self.campaigns[cid]

    def record_qualified(self, provider_id: str) -> None:
        c = self.get_provider(provider_id)
        if c:
            c.qualified_opportunities += 1

    def can_spend(self, provider_id: str, amount: float) -> bool:
        c = self.get_provider(provider_id)
        return bool(c and c.state not in {CampaignState.ELIMINATED, CampaignState.PAUSED} and amount > 0 and c.remaining_usd >= amount)

    def spend(self, provider_id: str, amount: float) -> None:
        c = self.get_provider(provider_id)
        if not c or amount <= 0 or c.remaining_usd + 1e-12 < amount:
            raise ValueError("campaign balance")
        c.remaining_usd -= amount
        c.spend_usd += amount

    def record_appearance(self, provider_id: str, task: str, opponents: Iterable[str]) -> None:
        c = self.get_provider(provider_id)
        if not c:
            return
        c.blind_appearances += 1
        d = c.task_stats.setdefault(task, {"appear":0.0,"first":0.0,"finalist":0.0,"purchase":0.0,"success":0.0,"outcomes":0.0})
        d["appear"] += 1
        for opp in opponents:
            if opp == provider_id:
                continue
            o = c.opponent_stats.setdefault(opp, {"appear":0.0,"win":0.0,"loss":0.0})
            o["appear"] += 1
        if c.state == CampaignState.UNSEEN:
            c.state = CampaignState.SEEDED
        elif c.state == CampaignState.SEEDED and c.blind_appearances >= 5:
            c.state = CampaignState.CHALLENGER

    def record_feedback(self, provider_id: str, task: str, *, finalist: bool=False, first: bool=False,
                        revealed: bool=False, purchased: bool=False, worst: bool=False,
                        success: bool | None=None, opponents_beaten: Iterable[str]=(), opponents_lost: Iterable[str]=()) -> None:
        c = self.get_provider(provider_id)
        if not c:
            return
        d = c.task_stats.setdefault(task, {"appear":0.0,"first":0.0,"finalist":0.0,"purchase":0.0,"success":0.0,"outcomes":0.0})
        if finalist:
            c.finalist_count += 1; d["finalist"] += 1
        if first:
            c.first_choice_count += 1; d["first"] += 1
        if revealed:
            c.reveal_count += 1
        if purchased:
            c.purchases += 1; d["purchase"] += 1
        if worst:
            c.worst_count += 1
        if success is not None:
            c.outcomes_reported += 1; d["outcomes"] += 1
            if success:
                c.successes += 1; d["success"] += 1
        for opp in opponents_beaten:
            o = c.opponent_stats.setdefault(opp, {"appear":0.0,"win":0.0,"loss":0.0}); o["win"] += 1
        for opp in opponents_lost:
            o = c.opponent_stats.setdefault(opp, {"appear":0.0,"win":0.0,"loss":0.0}); o["loss"] += 1
        self._transition(c)

    def _transition(self, c: ProviderCampaign) -> None:
        n = c.blind_appearances
        if n < self.cfg.min_eliminate_trials:
            return
        lo, hi = wilson_interval(c.first_choice_count, n, self.cfg.confidence_eliminate_z)
        # Strong evidence it is rarely first choice: stop subsidized blind exposure.
        if hi < 0.20 and c.conversion() < 0.10:
            c.state = CampaignState.ELIMINATED
            return
        if n >= self.cfg.min_organic_trials and lo > self.cfg.organic_win_threshold:
            c.state = CampaignState.ORGANIC
            return
        if c.remaining_usd <= 1e-12:
            c.state = CampaignState.PAUSED

    def marginal_trial_multiplier(self, provider_id: str) -> float:
        """More evidence + decisive losses => each additional subsidized trial costs more."""
        c = self.get_provider(provider_id)
        if not c:
            return 1.0
        n = c.blind_appearances
        base = 1.0 + math.log1p(n) / 3.0
        if n >= self.cfg.min_eliminate_trials:
            _, hi = wilson_interval(c.first_choice_count, n, self.cfg.confidence_eliminate_z)
            if hi < 0.35:
                base *= 2.0
        return base

    def dashboard(self, provider_id: str) -> dict:
        c = self.get_provider(provider_id)
        if not c:
            raise KeyError(provider_id)
        out = asdict(c)
        out["first_choice_rate"] = c.first_choice_rate()
        out["purchase_rate"] = c.conversion()
        out["success_rate"] = c.success_rate()
        out["research_efficiency"] = c.first_choice_count / c.spend_usd if c.spend_usd > 0 else None
        return out
