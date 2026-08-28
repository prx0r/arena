from __future__ import annotations
from collections import defaultdict
import math, random


class VOIThompson:
    """Thompson exploitation plus explicit information-value exploration bonus."""
    name = "voi_thompson"
    def __init__(self, prices, *, seed=7, exploration=0.15, gamma=0.995):
        self.prices=prices; self.rng=random.Random(seed); self.exploration=exploration; self.gamma=gamma
        self.a=defaultdict(lambda:1.0); self.b=defaultdict(lambda:1.0); self.n=defaultdict(int)
    def choose(self, context, providers):
        task=context.get("task_type","unknown")
        maxp=max(self.prices[p] for p in providers) or 1
        def score(p):
            q=self.rng.betavariate(self.a[(task,p)],self.b[(task,p)])
            uncertainty=1/math.sqrt(1+self.n[(task,p)])
            cost=self.prices[p]/maxp
            return q - 0.12*cost + self.exploration*uncertainty
        return max(providers,key=score)
    def update(self, context, provider, quality, cost, failed):
        task=context.get("task_type","unknown")
        for p in self.prices:
            k=(task,p); self.a[k]=1+self.gamma*(self.a[k]-1); self.b[k]=1+self.gamma*(self.b[k]-1)
        r=0 if failed else max(0,min(1,quality)); k=(task,provider)
        self.a[k]+=r; self.b[k]+=1-r; self.n[k]+=1
