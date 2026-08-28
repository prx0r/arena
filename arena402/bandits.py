from __future__ import annotations

from dataclasses import dataclass
import math
import random
import time
from collections import defaultdict


@dataclass
class BetaBelief:
    alpha: float = 1.0
    beta: float = 1.0
    last_update: float = 0.0
    n_effective: float = 0.0

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def variance(self) -> float:
        a, b = self.alpha, self.beta
        return (a * b) / (((a + b) ** 2) * (a + b + 1.0))


class DiscountedContextualBeta:
    """Small, dependency-free contextual posterior used by simulation and MVP.

    It accepts soft rewards in [0,1]. Decay is applied lazily so old provider
    behavior stops dominating after an endpoint/model/version change.
    """

    def __init__(self, *, half_life_steps: float = 800.0, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        self.half_life_steps = half_life_steps
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self._b: dict[tuple[str, str, str], BetaBelief] = {}
        self._step = 0

    def _key(self, task: str, provider_id: str, version: str = "1") -> tuple[str, str, str]:
        return (task, provider_id, version)

    def _get(self, key: tuple[str, str, str]) -> BetaBelief:
        if key not in self._b:
            self._b[key] = BetaBelief(self.prior_alpha, self.prior_beta, float(self._step), 0.0)
        return self._b[key]

    def _decay(self, b: BetaBelief) -> None:
        elapsed = max(0.0, self._step - b.last_update)
        if elapsed <= 0:
            return
        factor = 0.5 ** (elapsed / max(self.half_life_steps, 1e-9))
        b.alpha = self.prior_alpha + (b.alpha - self.prior_alpha) * factor
        b.beta = self.prior_beta + (b.beta - self.prior_beta) * factor
        b.n_effective *= factor
        b.last_update = float(self._step)

    def tick(self, n: int = 1) -> None:
        self._step += n

    def update(self, task: str, provider_id: str, reward: float, *, weight: float = 1.0, version: str = "1") -> None:
        reward = min(1.0, max(0.0, reward))
        key = self._key(task, provider_id, version)
        b = self._get(key)
        self._decay(b)
        b.alpha += weight * reward
        b.beta += weight * (1.0 - reward)
        b.n_effective += weight
        b.last_update = float(self._step)

    def stats(self, task: str, provider_id: str, *, version: str = "1") -> tuple[float, float, float]:
        b = self._get(self._key(task, provider_id, version))
        self._decay(b)
        return b.mean, b.variance, b.n_effective

    def sample(self, task: str, provider_id: str, rng: random.Random, *, version: str = "1") -> float:
        b = self._get(self._key(task, provider_id, version))
        self._decay(b)
        return rng.betavariate(max(b.alpha, 1e-6), max(b.beta, 1e-6))

    def uncertainty(self, task: str, provider_id: str, *, version: str = "1") -> float:
        mean, var, n = self.stats(task, provider_id, version=version)
        # Map Beta variance to roughly [0,1], retain novelty pressure at low n.
        return min(1.0, math.sqrt(max(var, 0.0)) * 4.0 + 1.0 / math.sqrt(1.0 + n))


@dataclass(frozen=True)
class UtilityWeights:
    quality: float = 1.0
    cost: float = 0.18
    latency: float = 0.05
    failure: float = 0.6


def predicted_utility(
    quality: float,
    success: float,
    price_usd: float,
    latency_ms: float,
    *,
    max_price: float,
    max_latency_ms: float,
    weights: UtilityWeights = UtilityWeights(),
) -> float:
    cost_norm = price_usd / max(max_price, 1e-9)
    lat_norm = min(1.0, latency_ms / max(max_latency_ms, 1e-9))
    fail_prob = 1.0 - success
    raw = weights.quality * quality - weights.cost * cost_norm - weights.latency * lat_norm - weights.failure * fail_prob
    # Convert into a bounded score so conservative-regret rules have stable semantics.
    return 1.0 / (1.0 + math.exp(-3.0 * raw))


def information_value(*, uncertainty: float, demand: float, future_transfer: float, price_usd: float, novelty: float = 1.0) -> float:
    """Contextual IDS-inspired value proxy: future-useful information per cost."""
    numerator = max(0.0, uncertainty) * max(0.0, demand) * max(0.0, future_transfer) * max(0.0, novelty)
    return min(1.0, numerator / math.sqrt(max(price_usd, 1e-6)) * 0.04)


def sponsor_pressure(balance_usd: float, *, log_scale: float = 0.20, cap: float = 0.20) -> float:
    """Diminishing-return funding term. It is NEVER used in organic ranking."""
    if balance_usd <= 0:
        return 0.0
    return min(cap, log_scale * math.log1p(balance_usd) / math.log(101.0))
