from __future__ import annotations

from collections import Counter
from hashlib import blake2b
import math
import re

_TOKEN = re.compile(r"[a-z0-9_./:+-]+")


class HashingEmbedder:
    """Dependency-free signed feature hashing for cheap local semantic-ish retrieval.

    Production can replace this with an embedding API without changing the store/router.
    """

    def __init__(self, dims: int = 512, ngrams: bool = True):
        self.dims = dims
        self.ngrams = ngrams

    def _features(self, text: str) -> list[str]:
        toks = _TOKEN.findall(text.lower())
        feats = list(toks)
        if self.ngrams:
            feats += [f"{a}::{b}" for a, b in zip(toks, toks[1:])]
        return feats

    def embed(self, text: str) -> list[float]:
        v = [0.0] * self.dims
        counts = Counter(self._features(text))
        for feature, count in counts.items():
            h = blake2b(feature.encode(), digest_size=8).digest()
            idx = int.from_bytes(h[:4], "big") % self.dims
            sign = 1.0 if h[4] & 1 else -1.0
            v[idx] += sign * (1.0 + math.log(count))
        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / norm for x in v]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))
