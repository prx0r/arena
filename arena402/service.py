from __future__ import annotations

from .choice import validate_tournament
from .exploration import ValueOfInformationAllocator
from .preferences import BradleyTerry
from .retrieval import EvidenceRetriever


class ArenaService:
    def __init__(self, store):
        self.store=store
        self.retriever=EvidenceRetriever(store)
        self.allocator=ValueOfInformationAllocator(store)

    def recommend(self, query: str, k: int = 5, public_only: bool = False) -> dict:
        slate=self.retriever.search(query,k=k,public_only=public_only)
        return {
            "slate_id": slate.slate_id,
            "query": query,
            "blind": True,
            "items": [i.__dict__ for i in slate.items],
            "mechanic": "keep-up-to-2, reveal sequentially",
            "note": "Sponsor money never enters organic retrieval. Full pairwise edges are not inferred from one click.",
        }

    def choose(self, slate_id: str, blind_id: str, buyer_id: str = "anonymous") -> dict:
        item=self.store.record_choice(slate_id,blind_id,buyer_id)
        provider=self.store.provider(item["provider_id"])
        return {"observation_id":item["observation_id"],"provider":provider,"historical_cost_usd":item["cost_usd"],"direct_endpoint":None if not provider else provider["endpoint"]}

    def commit_tournament(self, slate_id: str, finalists: list[str], reveal_order: list[str], buyer_id: str="anonymous") -> dict:
        slate=self.store.get_slate(slate_id)
        if not slate: raise KeyError("slate")
        all_ids=[x["blind_id"] for x in slate["items"]]
        result=validate_tournament(all_ids,finalists,reveal_order)
        tiers=[list(x) for x in result.partial_order() if x]
        edges=self.store.record_partial_order(slate_id,tiers,buyer_id)
        reveals=[]
        for blind in reveal_order:
            item=next(x for x in slate["items"] if x["blind_id"]==blind)
            p=self.store.provider(item["provider_id"])
            reveals.append({"blind_id":blind,"provider":p,"historical_cost_usd":item["cost_usd"]})
        return {"partial_order":tiers,"pairwise_edges_recorded":edges,"reveals":reveals}

    def outcome(self, observation_id: str, success: bool, score: float | None=None, buyer_id: str="anonymous") -> dict:
        self.store.record_outcome(observation_id,success,score,buyer_id); return {"ok":True}

    def research_offer(self, query: str, provider_id: str) -> dict | None:
        p=self.store.provider(provider_id)
        if not p: raise KeyError("provider")
        offer=self.allocator.offer(query,provider_id,float(p["price_usd"]))
        return None if offer is None else offer.__dict__

    def preference_ranking(self) -> dict:
        bt=BradleyTerry().fit_counts(self.store.pairwise_counts())
        return dict(sorted(bt.skill.items(),key=lambda kv:kv[1],reverse=True))
