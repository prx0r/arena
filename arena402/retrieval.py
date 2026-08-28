from __future__ import annotations

import json
import secrets
import time
from collections import defaultdict

from collections import defaultdict
from .embedding import cosine
from .models import RecommendationItem, RecommendationSlate, stable_id


class EvidenceRetriever:
    """Buyer-facing evidence retrieval.

    Fairness invariant: historical quality, popularity, sponsor balances, and
    previous choices do not determine *eligibility*. They may be returned as
    downstream evidence but not used to prevent a relevant challenger from
    entering the experimental pool. This simple retriever is production-safe
    for the historical-example endpoint; the richer slate policy lives in
    arena402.slate.
    """

    def __init__(self, store, *, half_life_days: float = 45.0):
        self.store = store
        self.half_life_days = half_life_days

    def _freshness(self, created_at: float, now: float) -> float:
        age_days = max(0.0, (now - created_at) / 86400)
        return 0.5 ** (age_days / max(self.half_life_days, 1e-9))

    def search(self, query: str, k: int = 5, *, public_only: bool = False, mode: str = "recommend") -> RecommendationSlate:
        """D-optimal: 1 incumbent+1 closest+1 price+1 uncertain+NewSearch. mode=arena=no quality bias."""
        qv = self.store.embedder.embed(query)
        now = time.time()
        per_provider: dict[str, tuple[float, float, dict]] = {}
        provider_n: dict[str, int] = defaultdict(int)
        for r in self.store.observations():
            if public_only and not r["public_example"]:
                continue
            sim = max(-1.0, min(1.0, cosine(qv, json.loads(r["request_vec_json"]))))
            freshness = self._freshness(r["created_at"], now)
            quality = 0.5 if r["quality"] is None else float(r["quality"])
            if mode == "arena":
                score = 0.80 * sim + 0.20 * freshness
            else:
                score = 0.70 * sim + 0.20 * freshness + 0.10 * quality
            old = per_provider.get(r["provider_id"])
            if old is None or score > old[0]:
                per_provider[r["provider_id"]] = (score, sim, r)
            provider_n[r["provider_id"]] += 1

        ranked = sorted(per_provider.values(), key=lambda x: x[0], reverse=True)

        # D-optimal slot allocation: incumbent + closest + price + uncertain + challenger
        incumbent = ranked[0] if ranked else None
        closest = ranked[1] if len(ranked) > 1 else None
        cheapest = min(ranked, key=lambda x: x[2]["cost_usd"]) if ranked else None
        uncertain = max(ranked, key=lambda x: provider_n[x[2]["provider_id"]] if provider_n[x[2]["provider_id"]] > 0 else 999) if ranked else None
        challenger = ranked[-1] if len(ranked) > 2 else None

        # Deduplicate while preserving diversity
        seen = set()
        slots = []
        for candidate in [incumbent, closest, cheapest, uncertain, challenger]:
            if candidate and candidate[2]["provider_id"] not in seen:
                slots.append(candidate)
                seen.add(candidate[2]["provider_id"])
        # Fill remaining from ranked if needed
        for cand in ranked:
            if len(slots) >= k:
                break
            if cand[2]["provider_id"] not in seen:
                slots.append(cand)
                seen.add(cand[2]["provider_id"])
        selected = slots[:k]

        items=[]; hidden=[]
        for _,sim,r in selected:
            blind=secrets.token_urlsafe(6)
            item=RecommendationItem(
                blind_id=blind, observation_id=r["observation_id"], similarity=round(sim,5),
                historical_request=r["request_text"],
                output_preview=r["response_preview"] if r["public_example"] else "[private evidence: preview withheld]",
                cost_usd=float(r["cost_usd"]), latency_ms=float(r["latency_ms"]),
                evidence_quality=None if r["quality"] is None else float(r["quality"]),
                sample_age_days=max(0.0,(now-r["created_at"])/86400), task_type=r["task_type"],
            )
            items.append(item); hidden.append({**item.__dict__,"provider_id":r["provider_id"]})
        slate_id=stable_id("slate",{"query":query,"nonce":secrets.token_hex(8),"items":[i.observation_id for i in items]})
        self.store.save_slate(slate_id,query,hidden)
        return RecommendationSlate(slate_id=slate_id,query=query,items=tuple(items),created_at=now)
