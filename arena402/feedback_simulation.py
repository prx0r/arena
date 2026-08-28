from __future__ import annotations

"""Reproducible lab for buyer/scout feedback mechanics.

This is intentionally a *mechanism* simulation, not a claim about real agents.
Assumptions (effort cost, cheating probability, observation noise) are explicit
parameters and must be sensitivity-swept before production decisions.
"""

from dataclasses import dataclass
import itertools
import random
from statistics import mean


@dataclass(frozen=True)
class FeedbackConfig:
    k: int = 5
    observation_noise: float = 0.08
    compute_cost_per_item: float = 0.001
    base_low_effort_probability: float = 0.30
    consequential_low_effort_probability: float = 0.02
    scout_audit_rate: float = 0.10
    scout_reward_usd: float = 0.001


@dataclass(frozen=True)
class FeedbackEpisode:
    mechanism: str
    pairwise_edges: int
    pairwise_precision: float
    comparison_cost: float
    low_effort: bool
    information_per_cost: float


def _pairs_from_ranking(ranking:list[str])->list[tuple[str,str]]:
    return [(ranking[i],ranking[j]) for i in range(len(ranking)) for j in range(i+1,len(ranking))]


def _truth(values:dict[str,float],a:str,b:str)->bool:
    return values[a]>=values[b]


def _precision(edges:list[tuple[str,str]],values:dict[str,float])->float:
    if not edges:return 0.0
    return sum(1 for a,b in edges if _truth(values,a,b))/len(edges)


def run_feedback_episode(*,seed:int,mechanism:str,cfg:FeedbackConfig=FeedbackConfig())->FeedbackEpisode:
    rng=random.Random(seed)
    ids=[f"p{i}" for i in range(cfg.k)]
    latent={p:rng.random() for p in ids}

    if mechanism in {"favorite_reveal","tournament_5_2_1"}:
        low_prob=cfg.consequential_low_effort_probability
    elif mechanism=="best_worst_scout":
        # Audit probability makes low-effort submission risky for paid scouts.
        low_prob=cfg.base_low_effort_probability*(1-cfg.scout_audit_rate)
    else:
        low_prob=cfg.base_low_effort_probability
    low_effort=rng.random()<low_prob

    if low_effort:
        perceived=ids[:];rng.shuffle(perceived)
    else:
        perceived=sorted(ids,key=lambda p:latent[p]+rng.gauss(0,cfg.observation_noise),reverse=True)

    if mechanism=="favorite_reveal":
        # One consequential reveal: selected item is preferred to unrevealed alternatives.
        edges=[(perceived[0],p) for p in ids if p!=perceived[0]]
        response_units=1
    elif mechanism=="tournament_5_2_1":
        finalists=perceived[:2]; eliminated=[p for p in ids if p not in finalists]
        edges=[(finalists[0],finalists[1])]
        edges += [(x,y) for x in finalists for y in eliminated]
        response_units=2
    elif mechanism=="best_worst_scout":
        best,worst=perceived[0],perceived[-1]
        middle=[p for p in ids if p not in {best,worst}]
        edges=[(best,p) for p in ids if p!=best]
        edges += [(p,worst) for p in middle]
        response_units=2
    elif mechanism=="full_rank_scout":
        edges=_pairs_from_ranking(perceived)
        response_units=cfg.k
    else:
        raise ValueError(mechanism)

    # Cost is an abstract normalized comparison/compute burden. Paid scout reward
    # is added because it is a real mechanism cost to Arena.
    cost=cfg.compute_cost_per_item*cfg.k + 0.0005*response_units
    if mechanism.endswith("scout"):
        cost += cfg.scout_reward_usd
    precision=_precision(edges,latent)
    useful_edges=precision*len(edges)
    return FeedbackEpisode(mechanism,len(edges),precision,cost,low_effort,useful_edges/max(cost,1e-12))


def sweep_feedback(*,seeds=range(500),ks=(3,5,7,8),audit_rates=(0.0,0.05,0.10,0.25))->dict:
    out={}
    mechanisms=("favorite_reveal","tournament_5_2_1","best_worst_scout","full_rank_scout")
    for k in ks:
        for audit in audit_rates:
            cfg=FeedbackConfig(k=k,scout_audit_rate=audit)
            for mech in mechanisms:
                rs=[run_feedback_episode(seed=10_000*k+100*int(audit*100)+s,mechanism=mech,cfg=cfg) for s in seeds]
                out[f"k={k}|audit={audit}|{mech}"]={
                    "pairwise_edges_mean":mean(r.pairwise_edges for r in rs),
                    "pairwise_precision_mean":mean(r.pairwise_precision for r in rs),
                    "low_effort_rate":mean(float(r.low_effort) for r in rs),
                    "information_per_cost_mean":mean(r.information_per_cost for r in rs),
                }
    return out
