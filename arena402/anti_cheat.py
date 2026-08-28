from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from collections import defaultdict
import math


@dataclass(frozen=True)
class EvidenceFingerprint:
    buyer_wallet: str
    provider_wallet: str
    request_hash: str
    response_hash: str
    tx_hash: str | None
    timestamp_bucket: int


class AntiCheat:
    """Cheap first-line fraud scoring; not a Sybil oracle.

    Production should add graph clustering, wallet funding lineage, device/agent
    identity where consensual, and challenge tasks. This module keeps the core
    invariants deterministic and testable.
    """

    def __init__(self):
        self.pair_counts = defaultdict(int)
        self.request_counts = defaultdict(int)
        self.response_counts = defaultdict(int)
        self.tx_seen: set[str] = set()
        self.wallet_activity = defaultdict(int)

    def score(self, fp: EvidenceFingerprint) -> tuple[float, tuple[str, ...]]:
        risk = 0.0
        reasons: list[str] = []
        pair = (fp.buyer_wallet.lower(), fp.provider_wallet.lower())
        if fp.buyer_wallet.lower() == fp.provider_wallet.lower():
            risk += 0.95; reasons.append("self-dealing")
        if self.pair_counts[pair] >= 10:
            risk += min(0.60, 0.05 * math.log1p(self.pair_counts[pair])); reasons.append("repeated-wallet-pair")
        if self.request_counts[fp.request_hash] >= 5:
            risk += 0.25; reasons.append("request-reuse")
        if self.response_counts[fp.response_hash] >= 5:
            risk += 0.25; reasons.append("response-reuse")
        if fp.tx_hash and fp.tx_hash in self.tx_seen:
            risk = 1.0; reasons.append("transaction-replay")
        return min(1.0, risk), tuple(reasons)

    def record(self, fp: EvidenceFingerprint) -> None:
        pair = (fp.buyer_wallet.lower(), fp.provider_wallet.lower())
        self.pair_counts[pair] += 1
        self.request_counts[fp.request_hash] += 1
        self.response_counts[fp.response_hash] += 1
        self.wallet_activity[fp.buyer_wallet.lower()] += 1
        if fp.tx_hash:
            self.tx_seen.add(fp.tx_hash)


@dataclass
class ScoutReliability:
    alpha: float = 2.0
    beta: float = 2.0
    audited: int = 0

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def audit(self, passed: bool, weight: float = 1.0) -> None:
        self.audited += 1
        if passed: self.alpha += weight
        else: self.beta += weight

    def reward_multiplier(self) -> float:
        if self.audited < 3:
            return 0.35
        return max(0.05, min(1.0, (self.mean - 0.4) / 0.6))
