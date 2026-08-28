from __future__ import annotations

from dataclasses import dataclass
import itertools
import math
import random
from typing import Iterable

from .bandits import DiscountedContextualBeta, UtilityWeights, information_value, predicted_utility, sponsor_pressure
from .mechanism import MechanismConfig, ProviderArm, RequestContext, SlateCandidate
from .sponsor import CampaignBook
from .research_market import ResearchCandidate, ResearchSlotMarket


@dataclass(frozen=True)
class DemandModel:
    task_mass: dict[str, float]

    def demand(self, task: str) -> float:
        if not self.task_mass:
            return 0.5
        top = max(self.task_mass.values()) or 1.0
        return min(1.0, max(0.05, self.task_mass.get(task, 0.1) / top))


def compatible(ctx: RequestContext, p: ProviderArm, cfg: MechanismConfig) -> bool:
    if not p.healthy or p.price_usd > ctx.budget_usd:
        return False
    if ctx.task not in p.task_tags and "any" not in p.task_tags:
        return False
    if ctx.schema != "any" and ctx.schema not in p.schema_tags and "any" not in p.schema_tags:
        return False
    return True


def _similarity(ctx: RequestContext, p: ProviderArm) -> float:
    # Production adapter replaces this with request/evidence embedding similarity.
    if ctx.task in p.task_tags:
        return 0.95
    if "any" in p.task_tags:
        return 0.60
    return 0.0


def _det(matrix: list[list[float]]) -> float:
    a = [row[:] for row in matrix]
    n = len(a)
    out = 1.0
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(a[r][i]))
        if abs(a[pivot][i]) < 1e-12:
            return 0.0
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            out *= -1
        pv = a[i][i]
        out *= pv
        for r in range(i + 1, n):
            factor = a[r][i] / pv
            for c in range(i + 1, n):
                a[r][c] -= factor * a[i][c]
    return out


def d_efficiency(selected: list[SlateCandidate]) -> float:
    """Tiny Bayesian-D-optimal proxy: determinant of regularized feature Gram matrix."""
    if not selected:
        return 0.0
    xs = [[1.0, c.similarity, c.predicted_utility, c.uncertainty, min(1.0, c.information_value)] for c in selected]
    d = len(xs[0])
    gram = [[0.0] * d for _ in range(d)]
    for x in xs:
        for i in range(d):
            for j in range(d):
                gram[i][j] += x[i] * x[j]
    for i in range(d):
        gram[i][i] += 1e-3
    return max(0.0, _det(gram)) ** (1.0 / d)


class SeparatedSlatePolicy:
    """Organic recommendation and paid experimental exposure are explicitly separated."""

    def __init__(self, beliefs: DiscountedContextualBeta, campaigns: CampaignBook, demand: DemandModel,
                 cfg: MechanismConfig | None = None, *, seed: int = 7, utility_weights: UtilityWeights = UtilityWeights()):
        self.beliefs = beliefs
        self.campaigns = campaigns
        self.demand_model = demand
        self.cfg = cfg or MechanismConfig()
        self.rng = random.Random(seed)
        self.utility_weights = utility_weights
        self.task_exposure: dict[tuple[str, str], int] = {}
        self.task_total: dict[str, int] = {}

    def score_pool(self, ctx: RequestContext, providers: Iterable[ProviderArm]) -> list[SlateCandidate]:
        providers = list(providers)
        max_price = max((p.price_usd for p in providers if compatible(ctx, p, self.cfg)), default=max(ctx.budget_usd, 1e-6))
        out: list[SlateCandidate] = []
        for p in providers:
            if not compatible(ctx, p, self.cfg):
                continue
            self.campaigns.record_qualified(p.provider_id)
            sim = _similarity(ctx, p)
            if sim < self.cfg.similarity_floor:
                continue
            q, var, n = self.beliefs.stats(ctx.task, p.provider_id, version=p.version)
            unc = self.beliefs.uncertainty(ctx.task, p.provider_id, version=p.version)
            # Until real latency model exists, provider metadata supplies rolling median.
            latency = float(p.metadata.get("latency_ms", 1200.0))
            success = float(p.metadata.get("success_prior", q))
            util = predicted_utility(q, success, p.price_usd, latency, max_price=max_price,
                                     max_latency_ms=ctx.max_latency_ms, weights=self.utility_weights)
            demand = self.demand_model.demand(ctx.task)
            novelty = 1.0 / math.sqrt(1.0 + n)
            info = information_value(uncertainty=unc, demand=demand, future_transfer=sim, price_usd=p.price_usd, novelty=novelty)
            # Organic score contains no sponsor term by invariant.
            organic = 0.62 * util + 0.23 * sim + 0.10 * success + 0.05 * (1.0 - min(1.0, p.price_usd / max_price))
            camp = self.campaigns.get_provider(p.provider_id)
            sponsor = sponsor_pressure(camp.remaining_usd if camp else 0.0,
                                       log_scale=self.cfg.sponsor_log_scale, cap=self.cfg.max_sponsor_component)
            exposure_share = self.task_exposure.get((ctx.task, p.provider_id), 0) / max(1, self.task_total.get(ctx.task, 0))
            fairness = max(0.0, 1.0 - exposure_share / max(self.cfg.max_exposure_share_per_task, 1e-9))
            # Research quality is scientific value; sponsor money is kept as a
            # separate component and never mixed into this base score.
            experimental = 0.62 * info + 0.25 * unc + 0.13 * sim
            experimental *= fairness
            out.append(SlateCandidate(
                provider_id=p.provider_id, evidence_id="", similarity=sim,
                predicted_utility=util, predicted_success=success, uncertainty=unc,
                information_value=info, diversity_gain=0.0,
                organic_score=organic, experimental_score=experimental,
                sponsor_component=sponsor,
            ))
        return out

    def adaptive_k(self, pool: list[SlateCandidate]) -> int:
        if not pool:
            return 0
        mean_unc = sum(c.uncertainty for c in pool) / len(pool)
        utility_spread = max(c.predicted_utility for c in pool) - min(c.predicted_utility for c in pool)
        info = max(c.information_value for c in pool)
        need = 0.50 * mean_unc + 0.30 * info + 0.20 * min(1.0, utility_spread * 2.0)
        raw = self.cfg.min_k + round(need * (self.cfg.max_k - self.cfg.min_k))
        # Each extra item imposes token/comparison cost; high cost pulls K toward minimum.
        cost_penalty = round(self.cfg.comparison_cost_per_item * max(0, raw - self.cfg.min_k) * 10)
        return max(self.cfg.min_k, min(self.cfg.max_k, raw - cost_penalty, len(pool)))

    def choose_slate(self, ctx: RequestContext, providers: Iterable[ProviderArm], *, force_k: int | None = None,
                     research_mode: str = "posted_price") -> list[SlateCandidate]:
        pool = self.score_pool(ctx, providers)
        if not pool:
            return []
        k = force_k if force_k is not None else self.adaptive_k(pool)
        k = max(1, min(k, len(pool)))
        baseline = sorted(pool, key=lambda c: c.organic_score, reverse=True)

        # Reserve at most one research slot. Organic slots are buyer-utility first.
        n_exp = min(self.cfg.experimental_slots_max, max(0, k - 2))
        organic_n = k - n_exp
        selected = baseline[:organic_n]
        selected_ids = {c.provider_id for c in selected}

        if n_exp:
            baseline_floor = min((c.predicted_utility for c in selected), default=0.0)
            safe_floor = baseline_floor * (1.0 - self.cfg.conservative_regret_budget)
            experimentals = [c for c in pool if c.provider_id not in selected_ids and c.predicted_utility >= safe_floor]
            if experimentals:
                market = ResearchSlotMarket(seed=self.rng.randrange(2**31))
                research_candidates=[]
                by_id={c.provider_id:c for c in experimentals}
                for c in experimentals:
                    camp=self.campaigns.get_provider(c.provider_id)
                    # V1 provider-funded research slot: an active campaign is
                    # required. Arena-funded exploration can be modeled as a
                    # separate virtual campaign rather than silently minting budget.
                    if camp is None or camp.remaining_usd <= 0:
                        continue
                    share=self.task_exposure.get((ctx.task,c.provider_id),0)/max(1,self.task_total.get(ctx.task,0))
                    safety=1.0 if c.predicted_utility>=safe_floor else 0.0
                    research_candidates.append(ResearchCandidate(
                        provider_id=c.provider_id,
                        relevance=c.similarity,
                        information_value=c.information_value,
                        conservative_safety=safety,
                        remaining_budget_usd=camp.remaining_usd,
                        marginal_trial_multiplier=self.campaigns.marginal_trial_multiplier(c.provider_id),
                        exposure_share=share,
                        # Soft auction is experimental. The campaign's per-trial
                        # willingness is capped to avoid a rich provider buying a
                        # recommendation rather than an experiment.
                        explicit_bid_usd=min(0.02,max(0.001,camp.remaining_usd/500.0)),
                    ))
                allocation = (market.allocate_soft_auction(research_candidates)
                              if research_mode == "soft_auction"
                              else market.allocate_posted_price(research_candidates))
                if allocation is not None:
                    best=by_id[allocation.provider_id]
                    # D-efficiency is a secondary diagnostic: the market's
                    # allocation already chose the scientifically useful arm.
                    div=min(1.0,d_efficiency(selected+[best]))
                    best=SlateCandidate(**{**best.__dict__,"role":"experimental","diversity_gain":div,
                                           "research_charge_usd":allocation.charge_usd,
                                           "research_mechanism":allocation.mechanism})
                    # Charge only the experimental campaign, never buyer ranking.
                    if self.campaigns.can_spend(best.provider_id,allocation.charge_usd):
                        self.campaigns.spend(best.provider_id,allocation.charge_usd)
                        selected.append(best)

        # If no funded/safe research experiment fills the slate, fall back to
        # organic leaders. This is important: lack of sponsor funding must not
        # degrade buyer utility just to satisfy an exploration quota.
        for c in baseline:
            if len(selected) >= k:
                break
            if c.provider_id not in {x.provider_id for x in selected}:
                selected.append(c)

        # Randomize blind positions. In production the exact policy probability
        # must be logged. The current deterministic lab uses the known uniform
        # position probability and a conservative inclusion proxy.
        self.rng.shuffle(selected)
        inc = min(1.0, k / max(1, len(pool)))
        pos = 1.0 / len(selected)
        selected = [SlateCandidate(**{**c.__dict__,"inclusion_probability":inc,"position_probability":pos}) for c in selected]
        self.task_total[ctx.task]=self.task_total.get(ctx.task,0)+1
        for c in selected:
            if c.role=="experimental":
                key=(ctx.task,c.provider_id)
                self.task_exposure[key]=self.task_exposure.get(key,0)+1
        return selected
