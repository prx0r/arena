from __future__ import annotations
from collections import defaultdict
import random


class ReplayMarket:
    def __init__(self, rows: list[dict], seed: int = 7):
        self.rng=random.Random(seed)
        self.by_task_provider=defaultdict(list)
        self.task_meta={}
        for r in rows:
            self.by_task_provider[(r["task_id"],r["provider_id"])].append(r)
            self.task_meta[r["task_id"]]=r
        self.tasks=list(self.task_meta)
        self.providers=sorted({r["provider_id"] for r in rows})
        self.prices={p: min(r["cost_usd"] for r in rows if r["provider_id"]==p) for p in self.providers}
    def sample(self, task_id, provider):
        xs=self.by_task_provider[(task_id,provider)]
        return self.rng.choice(xs)
    def oracle(self, task_id, cost_weight=0.0):
        best=None
        for p in self.providers:
            xs=self.by_task_provider[(task_id,p)]
            q=sum(x["quality"]*(0 if x["failed"] else 1) for x in xs)/len(xs)
            c=sum(x["cost_usd"] for x in xs)/len(xs)
            score=q-cost_weight*c
            if best is None or score>best[0]: best=(score,p,q,c)
        return best


def run_policy(rows, policy, *, rounds=10000, seed=7, cost_weight=0.0):
    m=ReplayMarket(rows,seed)
    rng=random.Random(seed)
    qs=[]; costs=[]; regrets=[]; chosen=defaultdict(int)
    for _ in range(rounds):
        tid=rng.choice(m.tasks)
        meta=m.task_meta[tid]
        context={"task_id":tid,"task_type":meta["task_type"],"task_text":meta["task_text"]}
        p=policy.choose(context,m.providers)
        r=m.sample(tid,p)
        q=0.0 if r["failed"] else r["quality"]
        policy.update(context,p,q,r["cost_usd"],r["failed"])
        oracle=m.oracle(tid,cost_weight)
        qs.append(q); costs.append(r["cost_usd"]); regrets.append(max(0.0,oracle[0]-(q-cost_weight*r["cost_usd"])))
        chosen[p]+=1
    return {
        "policy": policy.name, "rounds": rounds, "mean_quality": sum(qs)/len(qs), "spend_usd": sum(costs),
        "quality_per_dollar": sum(qs)/max(sum(costs),1e-12), "mean_regret": sum(regrets)/len(regrets),
        "provider_share": {p:n/rounds for p,n in chosen.items()},
    }
