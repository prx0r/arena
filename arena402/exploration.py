from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import math
import time

from .embedding import cosine
from .models import SubsidyOffer, stable_id


@dataclass(frozen=True)
class VOIConfig:
    max_subsidy_fraction: float = 0.90
    max_subsidy_usd: float = 0.05
    min_voi: float = 0.18
    demand_window_days: float = 30.0
    freshness_half_life_days: float = 30.0


class ValueOfInformationAllocator:
    """Heuristic active-learning budget allocator.

    Providers may fund experiments, never ranking. Ranking never reads sponsor balance.
    """

    def __init__(self, store, cfg: VOIConfig | None = None):
        self.store = store
        self.cfg = cfg or VOIConfig()

    def score(self, request_text: str, provider_id: str) -> tuple[float, dict]:
        qv = self.store.embedder.embed(request_text)
        now = time.time()
        similar = []
        provider_similar = []
        for r in self.store.observations():
            sim = max(0.0, cosine(qv, __import__("json").loads(r["request_vec_json"])))
            if sim < 0.20:
                continue
            age_days = max(0.0, (now-r["created_at"])/86400)
            w = sim * (0.5 ** (age_days/self.cfg.freshness_half_life_days))
            similar.append((w, r))
            if r["provider_id"] == provider_id:
                provider_similar.append((w, r))
        total_mass = sum(w for w, _ in similar)
        provider_mass = sum(w for w, _ in provider_similar)
        novelty = 1.0 / math.sqrt(1.0 + provider_mass)
        demand = min(1.0, math.log1p(total_mass) / math.log(25.0)) if total_mass else 0.35

        qualities = [float(r["quality"]) for w, r in provider_similar if r["quality"] is not None and w > 0]
        if len(qualities) >= 2:
            mean = sum(qualities)/len(qualities)
            variance = sum((x-mean)**2 for x in qualities)/(len(qualities)-1)
            uncertainty = min(1.0, math.sqrt(variance + 1/(len(qualities)+1)))
        else:
            uncertainty = 1.0

        freshest_age = min((max(0.0, (now-r["created_at"])/86400) for _, r in provider_similar), default=365.0)
        staleness = 1.0 - 0.5 ** (freshest_age / self.cfg.freshness_half_life_days)
        coverage_gap = 1.0 / math.sqrt(1.0 + len(provider_similar))
        voi = 0.30*novelty + 0.25*uncertainty + 0.20*demand + 0.15*staleness + 0.10*coverage_gap
        return min(1.0, voi), {
            "novelty": novelty, "uncertainty": uncertainty, "demand": demand,
            "staleness": staleness, "coverage_gap": coverage_gap,
            "similar_evidence": len(similar), "provider_similar_evidence": len(provider_similar),
        }

    def offer(self, request_text: str, provider_id: str, normal_price_usd: float) -> SubsidyOffer | None:
        balance = self.store.provider_fund(provider_id)
        if balance <= 0:
            return None
        voi, parts = self.score(request_text, provider_id)
        if voi < self.cfg.min_voi:
            return None
        desired = min(
            self.cfg.max_subsidy_usd,
            normal_price_usd*self.cfg.max_subsidy_fraction,
            normal_price_usd*voi,
            balance,
        )
        if desired <= 0:
            return None
        now = time.time()
        reason = ", ".join(f"{k}={v:.2f}" for k, v in parts.items() if isinstance(v, float))
        oid = stable_id("sub", {"q": request_text, "p": provider_id, "t": int(now//60)})
        return SubsidyOffer(
            offer_id=oid,
            provider_id=provider_id,
            normal_price_usd=normal_price_usd,
            subsidy_usd=desired,
            buyer_price_usd=max(0.0, normal_price_usd-desired),
            value_of_information=voi,
            reason=reason,
            expires_at=now+600,
        )
