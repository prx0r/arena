"""Reference FastAPI surface for the mechanism; core remains dependency-free."""
from __future__ import annotations

from dataclasses import asdict
from .evidence_market import CoverageBook, EvidenceMarket
from .mechanism import EvidenceGrade


def create_app(beliefs, provider_registry, recommender):
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
    except Exception as e:
        raise RuntimeError("install arena402[server]") from e

    app=FastAPI(title="402Arena Mechanism API",version="0.2.0")
    coverage=CoverageBook(); market=EvidenceMarket(coverage,lambda t,p:beliefs.uncertainty(t,p))

    class RecommendReq(BaseModel):
        request: str; task: str; budget_usd: float=0.02
    class QuoteReq(BaseModel):
        task: str; provider_id: str; grade: EvidenceGrade
        request_hash: str; response_hash: str; receipt_hash: str|None=None
    class BountyReq(BaseModel):
        request_id: str; task: str; provider_id: str

    @app.post("/v2/recommend")
    def recommend(req: RecommendReq):
        return recommender(req.model_dump())

    @app.post("/v2/evidence/quote")
    def quote(req: QuoteReq):
        q=market.quote_organic(req.task,req.provider_id,grade=req.grade,request_hash=req.request_hash,response_hash=req.response_hash,receipt_hash=req.receipt_hash)
        return asdict(q)

    @app.post("/v2/bounties")
    def bounty(req: BountyReq):
        p=provider_registry.get(req.provider_id)
        if not p: raise HTTPException(404,"provider")
        b=market.issue_bounty(request_id=req.request_id,task=req.task,provider_id=req.provider_id,provider_cost_usd=p.price_usd)
        return None if b is None else asdict(b)

    return app
