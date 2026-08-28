from __future__ import annotations

"""Contextual preference learning for 402Arena.

The core model deliberately separates:
- pre-price blind quality preference;
- post-price economic choice;
- task-local provider effects;
- global provider effects.

It is intentionally lightweight and deterministic so it can run inside Cogym
replays without numpy/scipy. Production can replace the optimizer while keeping
this interface and the logged sufficient statistics.
"""

from collections import defaultdict
from dataclasses import dataclass
import math
from typing import Iterable


@dataclass(frozen=True)
class PreferenceObservation:
    task: str
    winner: str
    loser: str
    weight: float = 1.0
    pre_price: bool = True
    source: str = "blind-choice"


class ContextualBradleyTerry:
    """Online hierarchical Bradley-Terry model.

    logit P(a>b | task) =
        global[a] - global[b]
      + task_effect[task,a] - task_effect[task,b]

    Separate model instances should be used for blind/pre-price preference and
    post-price economic preference. That prevents price from leaking into the
    quality model.
    """

    def __init__(self, *, lr: float = 0.045, l2_global: float = 0.001,
                 l2_task: float = 0.004, task_share: float = 0.70):
        self.lr = float(lr)
        self.l2_global = float(l2_global)
        self.l2_task = float(l2_task)
        self.task_share = min(1.0, max(0.0, float(task_share)))
        self.global_skill: dict[str, float] = defaultdict(float)
        self.task_skill: dict[tuple[str, str], float] = defaultdict(float)
        self.n: dict[tuple[str, str], float] = defaultdict(float)

    @staticmethod
    def _sigmoid(x: float) -> float:
        if x >= 0:
            z = math.exp(-x)
            return 1.0 / (1.0 + z)
        z = math.exp(x)
        return z / (1.0 + z)

    def score(self, task: str, provider: str) -> float:
        return self.global_skill[provider] + self.task_share * self.task_skill[(task, provider)]

    def win_prob(self, task: str, a: str, b: str) -> float:
        return self._sigmoid(self.score(task, a) - self.score(task, b))

    def uncertainty(self, task: str, provider: str) -> float:
        # Deterministic monotone proxy suitable for mechanism simulation.
        # Production should derive this from a posterior/ensemble.
        n = self.n[(task, provider)]
        return 1.0 / math.sqrt(1.0 + n / 4.0)

    def update(self, task: str, winner: str, loser: str, *, weight: float = 1.0) -> None:
        if winner == loser or weight <= 0:
            return
        p = self.win_prob(task, winner, loser)
        err = float(weight) * (1.0 - p)

        # Global shrinkage.
        gw = self.global_skill[winner]
        gl = self.global_skill[loser]
        global_fraction = 1.0 - self.task_share
        self.global_skill[winner] = gw + self.lr * (global_fraction * err - self.l2_global * gw)
        self.global_skill[loser] = gl + self.lr * (-global_fraction * err - self.l2_global * gl)

        # Task-local adaptation.
        kw, kl = (task, winner), (task, loser)
        tw, tl = self.task_skill[kw], self.task_skill[kl]
        self.task_skill[kw] = tw + self.lr * (self.task_share * err - self.l2_task * tw)
        self.task_skill[kl] = tl + self.lr * (-self.task_share * err - self.l2_task * tl)
        self.n[kw] += float(weight)
        self.n[kl] += float(weight)

    def update_partial_order(self, task: str, groups: Iterable[Iterable[str]], *, weight: float = 1.0) -> int:
        """Update only relations defensibly implied by ordered tiers.

        Example: [[E], [B], [A,C,D]] creates E>B; E>{A,C,D}; B>{A,C,D},
        but no relation among A/C/D.
        """
        tiers = [tuple(g) for g in groups]
        count = 0
        for i, better in enumerate(tiers):
            for worse in tiers[i + 1:]:
                for a in better:
                    for b in worse:
                        if a != b:
                            self.update(task, a, b, weight=weight)
                            count += 1
        return count

    def fit(self, rows: Iterable[PreferenceObservation]) -> "ContextualBradleyTerry":
        for row in rows:
            self.update(row.task, row.winner, row.loser, weight=row.weight)
        return self

    def ranking(self, task: str, providers: Iterable[str]) -> list[tuple[str, float]]:
        return sorted(((p, self.score(task, p)) for p in providers), key=lambda x: x[1], reverse=True)


class ContextualPlackettLuce:
    """Online rank-ordered logit for commissioned *full* rankings.

    Use this only when Arena explicitly commissions a ranking. Organic buyer
    interactions should be stored as partial orders and learned by
    ContextualBradleyTerry instead of fabricating inner ranks.
    """

    def __init__(self, *, lr: float = 0.035, l2: float = 0.003):
        self.lr = float(lr)
        self.l2 = float(l2)
        self.skill: dict[tuple[str, str], float] = defaultdict(float)
        self.n: dict[tuple[str, str], float] = defaultdict(float)

    def score(self, task: str, provider: str) -> float:
        return self.skill[(task, provider)]

    def update_ranking(self, task: str, ranking: list[str], *, weight: float = 1.0) -> None:
        """One SGD pass over the Plackett-Luce likelihood."""
        if len(set(ranking)) != len(ranking):
            raise ValueError("ranking contains duplicates")
        remaining = list(ranking)
        for chosen in ranking[:-1]:
            # Numerically stable softmax over the current remaining set.
            vals = {p: self.score(task, p) for p in remaining}
            m = max(vals.values())
            expv = {p: math.exp(vals[p] - m) for p in remaining}
            z = sum(expv.values()) or 1.0
            for p in remaining:
                target = 1.0 if p == chosen else 0.0
                prob = expv[p] / z
                key = (task, p)
                s = self.skill[key]
                self.skill[key] = s + self.lr * (weight * (target - prob) - self.l2 * s)
                self.n[key] += weight
            remaining.remove(chosen)

    def ranking(self, task: str, providers: Iterable[str]) -> list[tuple[str, float]]:
        return sorted(((p, self.score(task, p)) for p in providers), key=lambda x: x[1], reverse=True)
