from __future__ import annotations

from collections import defaultdict
import random


class PADCT:
    """Payment-aware discounted contextual Thompson sampler inspired by 402Pilot.

    This is an independent compact implementation: Beta quality beliefs per
    (task_type, provider), exponential discounting, and wallet-pressure tradeoff.
    """
    name = "pa_dct"

    def __init__(self, prices: dict[str, float], *, budget: float = 50.0, horizon: int = 10000,
                 gamma: float = 0.995, seed: int = 7):
        self.prices = prices
        self.budget = budget
        self.initial_budget = budget
        self.horizon = horizon
        self.gamma = gamma
        self.rng = random.Random(seed)
        self.alpha = defaultdict(lambda: 1.0)
        self.beta = defaultdict(lambda: 1.0)
        self.t = 0

    def _lambda(self) -> float:
        elapsed = max(1, self.t)
        expected_spend = self.initial_budget * elapsed / max(1, self.horizon)
        actual_spend = self.initial_budget - self.budget
        pressure = max(0.0, actual_spend - expected_spend) / max(self.initial_budget, 1e-9)
        return min(0.95, pressure * 5.0)

    def choose(self, context: dict, providers: list[str]) -> str:
        affordable = [p for p in providers if self.prices[p] <= self.budget]
        if not affordable:
            return min(providers, key=lambda p: self.prices[p])
        task = context.get("task_type", "unknown")
        lam = self._lambda()
        max_price = max(self.prices[p] for p in affordable) or 1.0
        def score(p):
            q = self.rng.betavariate(self.alpha[(task,p)], self.beta[(task,p)])
            c = self.prices[p]/max_price
            return (1-lam)*q - lam*c
        return max(affordable, key=score)

    def update(self, context, provider, quality, cost, failed):
        task = context.get("task_type", "unknown")
        # Discount all beliefs in the observed context.
        for p in self.prices:
            k=(task,p)
            self.alpha[k] = 1 + self.gamma*(self.alpha[k]-1)
            self.beta[k] = 1 + self.gamma*(self.beta[k]-1)
        reward = 0.0 if failed else max(0.0, min(1.0, quality))
        k=(task,provider)
        self.alpha[k] += reward
        self.beta[k] += 1-reward
        self.budget -= cost
        self.t += 1
