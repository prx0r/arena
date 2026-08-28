from __future__ import annotations

"""Granular campaign report intended for new x402 providers."""

from dataclasses import dataclass
from typing import Iterable

from .mechanism import ProviderCampaign, wilson_interval


@dataclass(frozen=True)
class CampaignTrial:
    request_id: str
    task: str
    provider_id: str
    opponents: tuple[str,...]
    inclusion_probability: float
    position_probability: float
    blind_rank: int | None = None
    slate_size: int | None = None
    finalist: bool = False
    revealed: bool = False
    current_price_usd: float | None = None
    purchased: bool = False
    downstream_success: bool | None = None
    organic: bool = False


def _rate(num:float,den:float)->float|None:
    return num/den if den else None


def build_provider_report(campaign:ProviderCampaign,trials:Iterable[CampaignTrial])->dict:
    rows=list(trials)
    pairwise={}
    task={}
    rank_hist={}
    organic=0
    for r in rows:
        if r.organic:organic+=1
        if r.blind_rank is not None:rank_hist[str(r.blind_rank)]=rank_hist.get(str(r.blind_rank),0)+1
        t=task.setdefault(r.task,{"appear":0,"finalist":0,"reveal":0,"purchase":0,"success":0,"outcomes":0})
        t["appear"]+=1; t["finalist"]+=int(r.finalist);t["reveal"]+=int(r.revealed);t["purchase"]+=int(r.purchased)
        if r.downstream_success is not None:
            t["outcomes"]+=1;t["success"]+=int(r.downstream_success)
        for opp in r.opponents:
            if r.blind_rank is None:continue
            p=pairwise.setdefault(opp,{"coappear":0,"wins":0,"losses":0,"unknown":0})
            p["coappear"]+=1
            # A trial record alone may not contain the opponent rank. Leave
            # pairwise credit unknown rather than fabricate a comparison.
            p["unknown"]+=1
    for v in task.values():
        v["finalist_rate"]=_rate(v["finalist"],v["appear"])
        v["purchase_rate"]=_rate(v["purchase"],v["appear"])
        v["success_rate"]=_rate(v["success"],v["outcomes"])
    lo,hi=wilson_interval(campaign.first_choice_count,campaign.blind_appearances) if campaign.blind_appearances else (0,1)
    # Price rejection = revealed but not purchased
    price_rejections = sum(1 for r in rows if r.revealed and not r.purchased)
    # Price-adjusted frontier: quality/$ where quality = first_choice_rate
    price_adj = campaign.first_choice_rate() / max(campaign.spend_usd / max(campaign.blind_appearances, 1), 1e-9) if campaign.blind_appearances else None
    # Confidence: Wilson CI width
    ci_width = hi - lo if campaign.blind_appearances else 1.0
    # Organic lift: organic exposures / total (how much traffic earned after experiments)
    total_exposures = campaign.blind_appearances + organic
    organic_lift = organic / max(total_exposures, 1)
    # Version drift placeholder (would need old version data)
    version_drift = None
    # Niche map: per task_type first_choice_rate + purchase_rate
    niche_map = {}
    for task_name, t in task.items():
        niche_map[task_name] = {
            "first_choice_rate": t.get("finalist_rate", 0),
            "purchase_rate": t.get("purchase_rate", 0),
            "appearances": t.get("appear", 0),
        }

    return {
        "campaign_id":campaign.campaign_id,
        "provider_id":campaign.provider_id,
        "version":campaign.version,
        "state":campaign.state.value,
        "budget":{"funded_usd":campaign.funded_usd,"spent_usd":campaign.spend_usd,"remaining_usd":campaign.remaining_usd},
        "funnel":{
            "qualified_opportunities":campaign.qualified_opportunities,
            "blind_appearances":campaign.blind_appearances,
            "finalists":campaign.finalist_count,
            "first_choices":campaign.first_choice_count,
            "reveals":campaign.reveal_count,
            "purchases":campaign.purchases,
            "outcomes_reported":campaign.outcomes_reported,
            "successes":campaign.successes,
            "first_choice_rate":campaign.first_choice_rate(),
            "first_choice_wilson_95":[lo,hi],
            "purchase_rate":campaign.conversion(),
            "success_rate":campaign.success_rate(),
            "price_rejections":price_rejections,
            "price_rejection_rate":_rate(price_rejections, campaign.reveal_count),
            "inclusion_propensity":_rate(campaign.blind_appearances, campaign.qualified_opportunities),
        },
        "rank_histogram":rank_hist,
        "task_breakdown":task,
        "opponents":campaign.opponent_stats or pairwise,
        "organic_exposures":organic,
        "organic_lift":organic_lift,
        "price_adjusted_frontier":price_adj,
        "confidence":{"ci_width":ci_width,"ci_95":[lo,hi]},
        "version_drift":version_drift,
        "niche_map":niche_map,
        "research_efficiency":{
            "usd_per_blind_appearance": campaign.spend_usd/campaign.blind_appearances if campaign.blind_appearances else None,
            "usd_per_purchase": campaign.spend_usd/campaign.purchases if campaign.purchases else None,
            "usd_per_success": campaign.spend_usd/campaign.successes if campaign.successes else None,
            "cost_per_finding": campaign.spend_usd/max(campaign.successes, 1),
        },
        "privacy_note":"Raw buyer requests are excluded unless the buyer explicitly permitted disclosure; production reports should default to derived task/constraint features.",
    }
