from __future__ import annotations
import argparse, json
from arena402.datasets import load_402pilot
from arena402.replay import ReplayMarket, run_policy
from arena402.policies.baselines import Cheapest, RandomPolicy, EmpiricalMean
from arena402.policies.padct import PADCT
from arena402.policies.voi import VOIThompson


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",required=True); ap.add_argument("--rounds",type=int,default=10000); ap.add_argument("--seed",type=int,default=7)
    a=ap.parse_args(); rows=load_402pilot(a.repo); market=ReplayMarket(rows,a.seed)
    policies=[
        RandomPolicy(a.seed), Cheapest(market.prices), EmpiricalMean(market.prices),
        PADCT(market.prices,budget=50,horizon=a.rounds,seed=a.seed),
        VOIThompson(market.prices,seed=a.seed),
    ]
    out=[run_policy(rows,p,rounds=a.rounds,seed=a.seed) for p in policies]
    print(json.dumps(out,indent=2))

if __name__=="__main__": main()
