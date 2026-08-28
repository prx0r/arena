from __future__ import annotations
import argparse, json
from arena402.datasets import load_402pilot
from arena402.replay import ReplayMarket, run_policy
from arena402.economics import SeededExplorer, inject_new_provider


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True)
    ap.add_argument("--rounds",type=int,default=10000)
    ap.add_argument("--budgets",default="0,1,5,10,25,50")
    ap.add_argument("--seed",type=int,default=7)
    a=ap.parse_args()
    rows=load_402pilot(a.repo)
    rows=inject_new_provider(rows,source_provider="P-premium",new_provider="P-new",price_usd=0.0015)
    market=ReplayMarket(rows,a.seed)
    results=[]
    for b in [float(x) for x in a.budgets.split(",")]:
        p=SeededExplorer(market.prices,b,seed=a.seed)
        r=run_policy(rows,p,rounds=a.rounds,seed=a.seed)
        r.update({"research_budget_usd":b,"subsidy_spend_usd":p.subsidy_spend,"forced_explorations":p.forced_explorations})
        results.append(r)
    print(json.dumps(results,indent=2))

if __name__=="__main__": main()
