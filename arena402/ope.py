from __future__ import annotations

"""Off-policy evaluation primitives for randomized Arena slates.

Every production slate must log the probability under the logging policy of the
observed action (and, for a slate, the displayed positions). These estimators are
used to evaluate new policies on historical traffic before exposing wallets to
those policies.
"""

from dataclasses import dataclass
import math
from typing import Iterable


@dataclass(frozen=True)
class OPEEstimate:
    estimate: float
    effective_n: float
    max_weight: float
    n: int


def _ratio(row: dict, clip: float | None = None) -> float:
    lp = float(row.get("logging_prob", 0.0))
    tp = float(row.get("target_prob", 0.0))
    if lp <= 0.0 or tp < 0.0:
        return 0.0
    w = tp / lp
    return min(w, clip) if clip is not None else w


def ips(rows: list[dict], *, clip: float | None = None) -> float:
    vals=[]
    for r in rows:
        if float(r.get("logging_prob",0.0)) <= 0: continue
        vals.append(float(r["reward"]) * _ratio(r, clip))
    return sum(vals)/len(vals) if vals else 0.0


def snips(rows: list[dict], *, clip: float | None = None) -> float:
    num=den=0.0
    for r in rows:
        if float(r.get("logging_prob",0.0)) <= 0: continue
        w=_ratio(r, clip)
        num += w*float(r["reward"]); den += w
    return num/den if den else 0.0


def doubly_robust(rows: list[dict], *, clip: float | None = None) -> float:
    vals=[]
    for r in rows:
        q_target=float(r.get("q_target",0.0))
        if float(r.get("logging_prob",0.0)) <= 0:
            vals.append(q_target); continue
        correction=_ratio(r, clip)*(float(r["reward"])-float(r.get("q_logged",0.0)))
        vals.append(q_target+correction)
    return sum(vals)/len(vals) if vals else 0.0


def switch_dr(rows: list[dict], *, tau: float = 10.0) -> float:
    """SWITCH-style DR: avoid explosive importance corrections above tau."""
    vals=[]
    for r in rows:
        q_target=float(r.get("q_target",0.0))
        lp=float(r.get("logging_prob",0.0))
        if lp <= 0:
            vals.append(q_target); continue
        w=_ratio(r)
        if w <= tau:
            vals.append(q_target + w*(float(r["reward"])-float(r.get("q_logged",0.0))))
        else:
            vals.append(q_target)
    return sum(vals)/len(vals) if vals else 0.0


def diagnostics(rows: list[dict], *, clip: float | None = None) -> OPEEstimate:
    ws=[_ratio(r,clip) for r in rows if float(r.get("logging_prob",0.0))>0]
    if not ws:
        return OPEEstimate(0.0,0.0,0.0,0)
    s=sum(ws); ss=sum(w*w for w in ws)
    ess=(s*s/ss) if ss else 0.0
    return OPEEstimate(snips(rows,clip=clip),ess,max(ws),len(ws))


def slate_joint_probability(item_probs: Iterable[float]) -> float:
    out=1.0
    for p in item_probs:
        p=float(p)
        if p <= 0 or p > 1:
            return 0.0
        out *= p
    return out


def slate_ips(rows: list[dict], *, clip: float | None = 50.0) -> float:
    """Joint-propensity IPS for logged ordered slates.

    Each row may supply logging_item_probs/target_item_probs. This deliberately
    uses the exact logged order. For very large slates, production should prefer
    a structured slate/cascade estimator because joint weights can explode.
    """
    converted=[]
    for r in rows:
        lp=slate_joint_probability(r.get("logging_item_probs",()))
        tp=slate_joint_probability(r.get("target_item_probs",()))
        if lp <= 0: continue
        converted.append({"reward":float(r["reward"]),"logging_prob":lp,"target_prob":tp})
    return ips(converted,clip=clip)
