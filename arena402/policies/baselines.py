from __future__ import annotations
import random
from collections import defaultdict


class Cheapest:
    name = "always_cheapest"
    def __init__(self, prices: dict[str, float]): self.prices = prices
    def choose(self, context, providers): return min(providers, key=lambda p: self.prices[p])
    def update(self, *args, **kwargs): pass


class RandomPolicy:
    name = "random"
    def __init__(self, seed=7): self.rng = random.Random(seed)
    def choose(self, context, providers): return self.rng.choice(providers)
    def update(self, *args, **kwargs): pass


class EmpiricalMean:
    name = "empirical_mean"
    def __init__(self, prices: dict[str, float], cost_weight: float = 0.15):
        self.prices, self.cost_weight = prices, cost_weight
        self.sums = defaultdict(float); self.n = defaultdict(int)
    def choose(self, context, providers):
        def score(p):
            mean = self.sums[p]/self.n[p] if self.n[p] else 0.65
            return mean - self.cost_weight*self.prices[p]
        return max(providers, key=score)
    def update(self, context, provider, quality, cost, failed):
        self.sums[provider] += 0.0 if failed else quality; self.n[provider] += 1
