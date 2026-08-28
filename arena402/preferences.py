from __future__ import annotations

import math
from collections import defaultdict


class BradleyTerry:
    """Small online Bradley-Terry ranker over blind preference edges."""

    def __init__(self, lr: float = 0.08, l2: float = 0.001):
        self.lr = lr
        self.l2 = l2
        self.skill = defaultdict(float)

    @staticmethod
    def sigmoid(x: float) -> float:
        if x >= 0:
            z = math.exp(-x)
            return 1 / (1 + z)
        z = math.exp(x)
        return z / (1 + z)

    def update(self, winner: str, loser: str, weight: float = 1.0) -> None:
        sw, sl = self.skill[winner], self.skill[loser]
        p = self.sigmoid(sw - sl)
        g = weight * (1.0 - p)
        self.skill[winner] = sw + self.lr * (g - self.l2 * sw)
        self.skill[loser] = sl + self.lr * (-g - self.l2 * sl)

    def fit_counts(self, rows: list[dict]) -> "BradleyTerry":
        for row in rows:
            self.update(row["winner_provider"], row["loser_provider"], float(row["wins"]))
        return self

    def win_prob(self, a: str, b: str) -> float:
        return self.sigmoid(self.skill[a] - self.skill[b])
