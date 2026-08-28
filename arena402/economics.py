from __future__ import annotations

from collections import defaultdict
import random


class SeededExplorer:
    """A small sponsor-funded cold-start policy for offline experiments.

    It never boosts ranking directly. Sponsor money can only buy observations.
    After evidence is observed, the normal empirical utility score decides.
    """

    name = "seeded_explorer"

    def __init__(self, prices: dict[str, float], sponsor_budget: float,
                 *, subsidy_fraction: float = 0.8, prior_quality: float = 0.65,
                 explore_strength: float = 0.18, cost_weight: float = 5.0, seed: int = 7):
        self.prices = prices
        self.sponsor_budget = sponsor_budget
        self.subsidy_fraction = subsidy_fraction
        self.prior_quality = prior_quality
        self.explore_strength = explore_strength
        self.cost_weight = cost_weight
        self.rng = random.Random(seed)
        self.sum_q = defaultdict(float)
        self.n = defaultdict(int)
        self.subsidy_spend = 0.0
        self.forced_explorations = 0

    def _mean(self, task: str, p: str) -> float:
        k = (task, p)
        return self.sum_q[k] / self.n[k] if self.n[k] else self.prior_quality

    def choose(self, context: dict, providers: list[str]) -> str:
        task = context.get("task_type", "unknown")
        max_price = max(self.prices[p] for p in providers) or 1.0

        # Information value proxy: unseen/rare provider in this context, discounted by call price.
        candidates = []
        for p in providers:
            n = self.n[(task, p)]
            uncertainty = 1.0 / ((n + 1) ** 0.5)
            subsidy = min(self.prices[p] * self.subsidy_fraction, self.sponsor_budget)
            voi = uncertainty / max(self.prices[p], 1e-9)
            candidates.append((voi, subsidy, p))
        candidates.sort(reverse=True)

        # Explore only while there is real sponsor budget and the information bonus is material.
        voi, subsidy, p_exp = candidates[0]
        if subsidy > 0 and self.rng.random() < min(0.5, self.explore_strength * voi * min(self.prices.values())):
            self.sponsor_budget -= subsidy
            self.subsidy_spend += subsidy
            self.forced_explorations += 1
            return p_exp

        def utility(p: str) -> float:
            empirical = self._mean(task, p)
            uncertainty = 1.0 / ((self.n[(task, p)] + 1) ** 0.5)
            cost = self.prices[p] / max_price
            return empirical + 0.04 * uncertainty - self.cost_weight * 0.01 * cost
        return max(providers, key=utility)

    def update(self, context, provider, quality, cost, failed):
        task = context.get("task_type", "unknown")
        k = (task, provider)
        self.sum_q[k] += 0.0 if failed else quality
        self.n[k] += 1


def inject_new_provider(rows: list[dict], *, source_provider: str = "P-premium",
                        new_provider: str = "P-new", price_usd: float = 0.0015,
                        task_types: set[str] | None = None, quality_multiplier: float = 1.0) -> list[dict]:
    """Create a controlled cold-start arm using recorded responses from an existing provider.

    This avoids inventing output quality. We reuse recorded source-provider outcomes but alter the
    provider identity and price, which lets us ask an economic question: how much exploration spend
    is required to discover a genuinely strong but initially unknown cheaper provider?
    """
    out = list(rows)
    for r in rows:
        if r["provider_id"] != source_provider:
            continue
        if task_types and r["task_type"] not in task_types:
            continue
        x = dict(r)
        x["provider_id"] = new_provider
        x["cost_usd"] = price_usd
        x["quality"] = max(0.0, min(1.0, float(x["quality"]) * quality_multiplier))
        out.append(x)
    return out
