from __future__ import annotations

from .service import ArenaService
from .store import Store


def create_app(db_path: str = "arena402.sqlite"):
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
    except ImportError as e:
        raise RuntimeError("Install arena402[server] to run the API") from e

    store=Store(db_path); svc=ArenaService(store); app=FastAPI(title="402Arena",version="0.1.0")

    class RecommendReq(BaseModel):
        query: str
        top_k: int = 5
        public_only: bool = False
    class ChooseReq(BaseModel):
        slate_id: str
        blind_id: str
        buyer_id: str = "anonymous"
    class OutcomeReq(BaseModel):
        observation_id: str
        success: bool
        score: float | None = None
        buyer_id: str = "anonymous"
    class FundReq(BaseModel):
        provider_id: str
        amount_usd: float
    class OfferReq(BaseModel):
        query: str
        provider_id: str

    @app.get("/healthz")
    def healthz(): return {"ok":True}
    @app.post("/recommend")
    def recommend(r: RecommendReq): return svc.recommend(r.query,max(1,min(20,r.top_k)),r.public_only)
    @app.post("/choose")
    def choose(r: ChooseReq):
        try: return svc.choose(r.slate_id,r.blind_id,r.buyer_id)
        except KeyError as e: raise HTTPException(404,str(e))
    @app.post("/outcome")
    def outcome(r: OutcomeReq): return svc.outcome(r.observation_id,r.success,r.score,r.buyer_id)
    @app.post("/provider/fund")
    def fund(r: FundReq): store.fund_provider(r.provider_id,r.amount_usd); return {"ok":True}
    @app.post("/research-credit")
    def credit(r: OfferReq): return {"offer": svc.research_offer(r.query,r.provider_id)}
    @app.get("/rank/preferences")
    def ranking(): return svc.preference_ranking()
    return app
