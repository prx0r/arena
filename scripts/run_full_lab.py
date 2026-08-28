from __future__ import annotations
import argparse,json
from pathlib import Path
from arena402.experiments import aggregate,run_policy_sweep,run_k_sweep,run_regret_budget_sweep,run_funding_sweep,run_evidence_bid_curve
from arena402.feedback_simulation import sweep_feedback


def main():
    ap=argparse.ArgumentParser(description="Run the complete deterministic 402Arena mechanism lab")
    ap.add_argument("--rounds",type=int,default=1200)
    ap.add_argument("--seeds",type=int,default=12)
    ap.add_argument("--out",default="experiments/results/full_lab.json")
    a=ap.parse_args()
    seeds=range(a.seeds)
    payload={
        "schema":"arena402-full-lab-v1",
        "rounds":a.rounds,
        "seeds":a.seeds,
        "policy_sweep":aggregate(run_policy_sweep(seeds=seeds,rounds=a.rounds)),
        "k_sweep":run_k_sweep(seeds=range(min(8,a.seeds)),rounds=min(800,a.rounds)),
        "regret_budget_sweep":run_regret_budget_sweep(seeds=range(min(8,a.seeds)),rounds=min(800,a.rounds)),
        "funding_sweep":run_funding_sweep(seeds=range(min(8,a.seeds)),rounds=min(1000,a.rounds)),
        "evidence_bid_curve":run_evidence_bid_curve(),
        "feedback_sweep":sweep_feedback(seeds=range(250)),
    }
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(payload,indent=2,sort_keys=True))
    print(p)

if __name__=="__main__":main()
