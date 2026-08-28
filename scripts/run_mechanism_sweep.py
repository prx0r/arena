from __future__ import annotations
import argparse, json
from pathlib import Path
from arena402.experiments import aggregate, run_policy_sweep, run_k_sweep, run_regret_budget_sweep


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--rounds",type=int,default=1200)
    p.add_argument("--seeds",type=int,default=10)
    p.add_argument("--out",default="experiments/results/mechanism_sweep.json")
    a=p.parse_args()
    results=run_policy_sweep(seeds=range(a.seeds),rounds=a.rounds)
    payload={
        "policy_sweep":aggregate(results),
        "k_sweep":run_k_sweep(seeds=range(max(3,min(8,a.seeds))),rounds=min(a.rounds,900)),
        "regret_budget_sweep":run_regret_budget_sweep(seeds=range(max(3,min(8,a.seeds))),rounds=min(a.rounds,900)),
        "raw":[r.__dict__ for r in results],
    }
    path=Path(a.out); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(payload,indent=2,sort_keys=True))
    print(json.dumps(payload["policy_sweep"],indent=2,sort_keys=True))

if __name__=="__main__": main()
