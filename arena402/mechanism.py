from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from hashlib import sha256
import json
import math
import time
from typing import Any, Iterable


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(prefix: str, value: Any) -> str:
    return f"{prefix}_{sha256(canonical_json(value).encode()).hexdigest()}"


class CampaignState(str, Enum):
    UNSEEN = "UNSEEN"
    SEEDED = "SEEDED"
    CHALLENGER = "CHALLENGER"
    ORGANIC = "ORGANIC"
    ELIMINATED = "ELIMINATED"
    PAUSED = "PAUSED"


class EvidenceGrade(str, Enum):
    A_PROVIDER_BOUND = "A_PROVIDER_BOUND"  # provider-signed/bound request+response hashes
    B_ARENA_OBSERVED = "B_ARENA_OBSERVED"  # Arena proxy observed full transaction
    C_BUYER_ATTESTED = "C_BUYER_ATTESTED"  # buyer claims payload, valid payment receipt
    D_UNVERIFIED = "D_UNVERIFIED"


class EvidenceOrigin(str, Enum):
    ORGANIC = "ORGANIC"
    ARENA_COMMISSIONED = "ARENA_COMMISSIONED"
    PROVIDER_SPONSORED = "PROVIDER_SPONSORED"
    SCOUT = "SCOUT"
    SYNTHETIC = "SYNTHETIC"


GRADE_WEIGHT = {
    EvidenceGrade.A_PROVIDER_BOUND: 1.00,
    EvidenceGrade.B_ARENA_OBSERVED: 0.90,
    EvidenceGrade.C_BUYER_ATTESTED: 0.55,
    EvidenceGrade.D_UNVERIFIED: 0.15,
}

ORIGIN_WEIGHT = {
    EvidenceOrigin.ORGANIC: 1.00,
    EvidenceOrigin.ARENA_COMMISSIONED: 0.90,
    EvidenceOrigin.PROVIDER_SPONSORED: 0.75,
    EvidenceOrigin.SCOUT: 0.55,
    EvidenceOrigin.SYNTHETIC: 0.35,
}


@dataclass(frozen=True)
class RequestContext:
    request_id: str
    text: str
    task: str
    budget_usd: float
    max_latency_ms: float = 60_000.0
    schema: str = "any"
    buyer_id: str = "anonymous"
    features: tuple[float, ...] = ()
    created_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ProviderArm:
    provider_id: str
    endpoint: str
    price_usd: float
    task_tags: tuple[str, ...]
    schema_tags: tuple[str, ...] = ("any",)
    healthy: bool = True
    version: str = "1"
    sponsor_balance_usd: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    request_id: str
    request_text: str
    task: str
    provider_id: str
    provider_version: str
    response: str
    cost_usd: float
    latency_ms: float
    quality: float | None
    downstream_success: bool | None
    created_at: float
    request_hash: str
    response_hash: str
    tx_hash: str | None = None
    receipt_hash: str | None = None
    grade: EvidenceGrade = EvidenceGrade.D_UNVERIFIED
    origin: EvidenceOrigin = EvidenceOrigin.ORGANIC
    public: bool = False

    @property
    def weight(self) -> float:
        return GRADE_WEIGHT[self.grade] * ORIGIN_WEIGHT[self.origin]


@dataclass(frozen=True)
class SlateCandidate:
    provider_id: str
    evidence_id: str
    similarity: float
    predicted_utility: float
    predicted_success: float
    uncertainty: float
    information_value: float
    diversity_gain: float
    organic_score: float
    experimental_score: float
    sponsor_component: float
    inclusion_probability: float = 0.0
    position_probability: float = 0.0
    role: str = "organic"
    research_charge_usd: float = 0.0
    research_mechanism: str = ""


@dataclass(frozen=True)
class BlindSlate:
    slate_id: str
    request_id: str
    candidates: tuple[SlateCandidate, ...]
    positions: tuple[str, ...]
    reveal_credits: int
    mechanism_version: str
    created_at: float


@dataclass(frozen=True)
class RevealEvent:
    slate_id: str
    buyer_id: str
    blind_id: str
    rank_index: int
    provider_id: str
    price_usd: float
    purchased: bool | None = None
    created_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class PartialPreference:
    context_task: str
    buyer_id: str
    preferred_provider: str
    other_provider: str
    strength: float
    source: str
    pre_price: bool
    created_at: float = field(default_factory=time.time)


@dataclass
class ProviderCampaign:
    campaign_id: str
    provider_id: str
    version: str
    funded_usd: float
    remaining_usd: float
    state: CampaignState = CampaignState.UNSEEN
    qualified_opportunities: int = 0
    blind_appearances: int = 0
    finalist_count: int = 0
    first_choice_count: int = 0
    reveal_count: int = 0
    purchases: int = 0
    outcomes_reported: int = 0
    successes: int = 0
    worst_count: int = 0
    spend_usd: float = 0.0
    task_stats: dict[str, dict[str, float]] = field(default_factory=dict)
    opponent_stats: dict[str, dict[str, float]] = field(default_factory=dict)

    def conversion(self) -> float:
        return self.purchases / self.blind_appearances if self.blind_appearances else 0.0

    def first_choice_rate(self) -> float:
        return self.first_choice_count / self.blind_appearances if self.blind_appearances else 0.0

    def success_rate(self) -> float | None:
        return self.successes / self.outcomes_reported if self.outcomes_reported else None


@dataclass(frozen=True)
class EvidenceQuote:
    quote_id: str
    evidence_kind: str
    bid_usd: float
    expires_at: float
    reasons: tuple[str, ...]
    required_grade: EvidenceGrade


@dataclass(frozen=True)
class Bounty:
    bounty_id: str
    request_id: str
    provider_id: str
    max_provider_cost_usd: float
    reimbursement_usd: float
    research_reward_usd: float
    deadline: float
    nonce: str
    required_grade: EvidenceGrade
    campaign_id: str | None = None

    @property
    def total_reward_usd(self) -> float:
        return self.reimbursement_usd + self.research_reward_usd

    @property
    def commitment(self) -> str:
        return stable_hash("bounty", asdict(self))


@dataclass(frozen=True)
class MechanismConfig:
    similarity_floor: float = 0.35
    min_k: int = 3
    normal_k: int = 5
    max_k: int = 8
    reveal_credits: int = 2
    comparison_cost_per_item: float = 0.006
    conservative_regret_budget: float = 0.05
    experimental_slots_max: int = 1
    sponsor_log_scale: float = 0.20
    max_sponsor_component: float = 0.20
    freshness_half_life_days: float = 30.0
    confidence_eliminate_z: float = 1.96
    min_eliminate_trials: int = 30
    min_organic_trials: int = 40
    organic_win_threshold: float = 0.58
    max_exposure_share_per_task: float = 0.25


def wilson_interval(wins: float, n: float, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return (0.0, 1.0)
    p = wins / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    radius = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - radius), min(1.0, center + radius))


def pairwise_from_partial_order(groups: Iterable[Iterable[str]], *, strength: float = 1.0) -> list[tuple[str, str, float]]:
    """Convert tiers, best to worst, into only defensible pairwise relations."""
    tiers = [tuple(g) for g in groups]
    out: list[tuple[str, str, float]] = []
    for i, better in enumerate(tiers):
        for worse in tiers[i + 1 :]:
            for a in better:
                for b in worse:
                    if a != b:
                        out.append((a, b, strength))
    return out
