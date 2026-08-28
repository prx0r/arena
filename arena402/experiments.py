from __future__ import annotations

from dataclasses import asdict
import json
import math
from pathlib import Path
from statistics import mean, pstdev
from typing import Iterable

from .mechanism import MechanismConfig
from .simulation import ArenaSimulation, SimResult


POLICIES = ("organic_only", "random_explore", "paid_rank_bad", "separated_ids", "soft_research_auction")


def run_policy_sweep(*, seeds: Iterable[int] = range(10), rounds: int = 1200,
                     policies: Iterable[str] = POLICIES, cfg: MechanismConfig | None = None) -> list[SimResult]:
    out=[]
    for p in policies:
        for seed in seeds:
            out.append(ArenaSimulation(seed=seed, policy=p, cfg=cfg).run(rounds))
    return out


def aggregate(results: Iterable[SimResult]) -> dict:
    by={}
    rows=list(results)
    for policy in sorted({r.policy for r in rows}):
        rs=[r for r in rows if r.policy==policy]
        def stat(name):
            xs=[getattr(r,name) for r in rs if getattr(r,name) is not None]
            return {"mean":mean(xs) if xs else None,"std":pstdev(xs) if len(xs)>1 else 0.0,"n":len(xs)}
        by[policy]={
            "mean_realized_quality":stat("mean_realized_quality"),
            "mean_buyer_utility":stat("mean_buyer_utility"),
            "buyer_spend_usd":stat("buyer_spend_usd"),
            "research_spend_usd":stat("research_spend_usd"),
            "newseed_appearances":stat("newseed_appearances"),
            "newseed_purchases":stat("newseed_purchases"),
            "newseed_organic_purchases":stat("newseed_organic_purchases"),
            "discovery_round":stat("discovery_round"),
            "avg_slate_k":stat("avg_slate_k"),
        }
    return by


def run_k_sweep(*, ks=(3,4,5,6,8), seeds=range(8), rounds=800) -> dict:
    """Force K by pinning min=normal=max and measure utility/information cost tradeoff."""
    out={}
    for k in ks:
        cfg=MechanismConfig(min_k=k,normal_k=k,max_k=k,comparison_cost_per_item=0.006)
        rs=[ArenaSimulation(seed=s,policy="separated_ids",cfg=cfg).run(rounds) for s in seeds]
        # The objective explicitly charges comparison cost so larger slates must earn their keep.
        utility=[r.mean_buyer_utility - cfg.comparison_cost_per_item*r.avg_slate_k for r in rs]
        discovery=[r.discovery_round if r.discovery_round is not None else rounds+1 for r in rs]
        out[str(k)]={
            "net_utility_mean":mean(utility),
            "discovery_round_mean":mean(discovery),
            "newseed_appearances_mean":mean(r.newseed_appearances for r in rs),
            "comparison_items_mean":mean(r.comparison_items for r in rs),
        }
    return out


def run_regret_budget_sweep(*, budgets=(0.0,0.02,0.05,0.10,0.20), seeds=range(8), rounds=800) -> dict:
    out={}
    for b in budgets:
        cfg=MechanismConfig(conservative_regret_budget=b)
        rs=[ArenaSimulation(seed=s,policy="separated_ids",cfg=cfg).run(rounds) for s in seeds]
        out[str(b)]={
            "quality":mean(r.mean_realized_quality for r in rs),
            "buyer_utility":mean(r.mean_buyer_utility for r in rs),
            "discovery_round":mean((r.discovery_round or rounds+1) for r in rs),
            "research_spend":mean(r.research_spend_usd for r in rs),
        }
    return out



def run_funding_sweep(*, budgets=(0,1,5,10,25,50,100,1000), seeds=range(8), rounds=1000, policy="separated_ids") -> dict:
    """How much research funding is needed to bootstrap a cold-start provider?"""
    from dataclasses import replace
    from .simulation import DEFAULT_MARKET
    out={}
    for budget in budgets:
        market=tuple(replace(p,sponsor_budget_usd=float(budget)) if p.provider_id=="newseed" else p for p in DEFAULT_MARKET)
        rs=[ArenaSimulation(seed=s,policy=policy,market=market).run(rounds) for s in seeds]
        discoveries=[r.discovery_round if r.discovery_round is not None else rounds+1 for r in rs]
        out[str(budget)]={
            "discovery_round_mean":mean(discoveries),
            "appearance_mean":mean(r.newseed_appearances for r in rs),
            "purchase_mean":mean(r.newseed_purchases for r in rs),
            "organic_purchase_mean":mean(r.newseed_organic_purchases for r in rs),
            "research_spend_mean":mean(r.research_spend_usd for r in rs),
            "buyer_utility_mean":mean(r.mean_buyer_utility for r in rs),
        }
    return out


def run_evidence_bid_curve(*, masses=(0,1,5,20,60,200,1000), uncertainty=(1.0,0.6,0.2)) -> dict:
    from .bandits import DiscountedContextualBeta
    from .evidence_market import CoverageBook, EvidenceMarket
    from .mechanism import EvidenceGrade
    out={}
    for unc in uncertainty:
        for mass in masses:
            coverage=CoverageBook();coverage.observe_demand("coding",200)
            coverage.mass[("coding","p")]=float(mass)
            market=EvidenceMarket(coverage,lambda t,p,unc=unc:unc)
            q=market.quote_organic("coding","p",grade=EvidenceGrade.B_ARENA_OBSERVED,request_hash=f"r-{mass}-{unc}",response_hash="s",receipt_hash=None)
            out[f"unc={unc}|mass={mass}"]={"bid_usd":q.bid_usd,"reasons":list(q.reasons)}
    return out

def write_results(path: str | Path, payload: dict) -> None:
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,indent=2,sort_keys=True))
