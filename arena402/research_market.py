from __future__ import annotations

"""Provider-funded research-slot market.

The market is intentionally separated from organic recommendation. Providers
may fund *qualified blind experiments*; they cannot purchase a higher organic
utility score. V1 is a posted-price mechanism. A soft auction is included only
as an experimental policy for Cogym simulation.
"""

from dataclasses import dataclass
import math
import random
from typing import Iterable


@dataclass(frozen=True)
class ResearchCandidate:
    provider_id: str
    relevance: float
    information_value: float
    conservative_safety: float
    remaining_budget_usd: float
    marginal_trial_multiplier: float
    exposure_share: float = 0.0
    explicit_bid_usd: float | None = None


@dataclass(frozen=True)
class ResearchAllocation:
    provider_id: str
    charge_usd: float
    selection_probability: float
    mechanism: str
    score: float


@dataclass(frozen=True)
class ResearchMarketConfig:
    base_trial_price_usd: float = 0.0010
    max_trial_price_usd: float = 0.10
    min_relevance: float = 0.45
    min_information_value: float = 0.08
    min_safety: float = 0.90
    sponsor_log_cap: float = 2.5
    max_exposure_share: float = 0.25
    softmax_temperature: float = 0.18


class ResearchSlotMarket:
    def __init__(self, cfg: ResearchMarketConfig | None = None, *, seed: int = 7):
        self.cfg=cfg or ResearchMarketConfig()
        self.rng=random.Random(seed)

    def eligible(self,c:ResearchCandidate)->bool:
        return (c.relevance>=self.cfg.min_relevance and
                c.information_value>=self.cfg.min_information_value and
                c.conservative_safety>=self.cfg.min_safety and
                c.remaining_budget_usd>0 and
                c.exposure_share<self.cfg.max_exposure_share)

    def posted_price(self,c:ResearchCandidate)->float:
        """Charge rises as evidence becomes less informative/decisive.

        High information value receives a cheaper experiment because Arena also
        benefits. Repeated trials become progressively more expensive via the
        campaign's marginal multiplier.
        """
        if not self.eligible(c):
            return math.inf
        info=max(0.05,c.information_value)
        price=self.cfg.base_trial_price_usd*c.marginal_trial_multiplier*(0.55+0.45/info)
        return min(self.cfg.max_trial_price_usd,max(self.cfg.base_trial_price_usd,price))

    def allocate_posted_price(self,candidates:Iterable[ResearchCandidate])->ResearchAllocation|None:
        xs=[]
        for c in candidates:
            price=self.posted_price(c)
            if math.isfinite(price) and c.remaining_budget_usd>=price:
                # No bid enters this score. Arena allocates the slot to the
                # experiment with the highest expected scientific value.
                score=c.relevance*c.information_value*c.conservative_safety*(1-c.exposure_share)
                xs.append((score,c,price))
        if not xs:return None
        score,c,price=max(xs,key=lambda x:x[0])
        return ResearchAllocation(c.provider_id,price,1.0,"posted-price-voi",score)

    def allocate_soft_auction(self,candidates:Iterable[ResearchCandidate])->ResearchAllocation|None:
        """Experimental research auction; never use this score for organic rank.

        Bid contribution is logarithmic and capped, so a $1000 budget cannot
        linearly dominate a $10 budget. The output logs the sampling probability
        for off-policy evaluation.
        """
        scored=[]
        for c in candidates:
            price=self.posted_price(c)
            if not math.isfinite(price):continue
            bid=max(price,float(c.explicit_bid_usd or price))
            if c.remaining_budget_usd<bid:continue
            sponsor=min(self.cfg.sponsor_log_cap,math.log1p(bid/max(self.cfg.base_trial_price_usd,1e-12)))
            score=(c.relevance*c.information_value*c.conservative_safety*(1-c.exposure_share))*(1+0.20*sponsor)
            scored.append((score,c,bid))
        if not scored:return None
        m=max(s for s,_,__ in scored); temp=max(1e-6,self.cfg.softmax_temperature)
        weights=[math.exp((s-m)/temp) for s,_,__ in scored]
        z=sum(weights); x=self.rng.random()*z; acc=0.0
        for (score,c,bid),w in zip(scored,weights):
            acc+=w
            if x<=acc:
                return ResearchAllocation(c.provider_id,bid,w/z,"soft-research-auction",score)
        score,c,bid=scored[-1]; return ResearchAllocation(c.provider_id,bid,weights[-1]/z,"soft-research-auction",score)
