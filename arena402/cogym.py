from __future__ import annotations
from dataclasses import asdict
from hashlib import sha256
import json
from .experiments import run_policy_sweep, aggregate


def cogym_available() -> bool:
    try:
        import cogym_kernel  # noqa
        return True
    except Exception:
        return False


def worldpack_manifest() -> dict:
    return {
        "kind":"arena402.mechanism_lab","version":"2",
        "description":"replayable mechanism-design lab for empirical x402 routing and research-market incentives",
        "metrics":["buyer_utility","realized_quality","research_spend_usd","discovery_round","paid_rank_corruption"],
        "hard_gates":["buyer_utility >= 0.70","paid_rank_corruption == 0"],
    }


def deterministic_experiment_receipt(*, seeds=range(10), rounds=1200) -> dict:
    rows=run_policy_sweep(seeds=seeds,rounds=rounds)
    payload={"worldpack":worldpack_manifest(),"rounds":rounds,"seeds":list(seeds),"aggregate":aggregate(rows),"raw":[asdict(r) for r in rows]}
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"))
    payload["run_id"]="arena_run_"+sha256(raw.encode()).hexdigest()
    return payload
