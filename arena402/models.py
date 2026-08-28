from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
from typing import Any
import json
import time


def stable_id(prefix: str, payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"{prefix}_{sha256(raw.encode()).hexdigest()[:24]}"


@dataclass(frozen=True)
class Provider:
    provider_id: str
    label: str
    endpoint: str
    price_usd: float = 0.0
    category: str = "unknown"
    endpoint_fingerprint: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Observation:
    request_text: str
    provider_id: str
    response_preview: str
    cost_usd: float
    latency_ms: float
    quality: float | None = None
    success: bool | None = None
    task_type: str = "unknown"
    created_at: float = field(default_factory=time.time)
    endpoint_fingerprint: str = ""
    source: str = "live"
    public_example: bool = False
    request_id: str = ""
    observation_id: str = ""

    def with_ids(self) -> "Observation":
        request_id = self.request_id or stable_id("req", {"text": self.request_text})
        oid = self.observation_id or stable_id(
            "obs",
            {
                "request_id": request_id,
                "provider": self.provider_id,
                "response": self.response_preview,
                "cost": self.cost_usd,
                "latency": self.latency_ms,
                "fingerprint": self.endpoint_fingerprint,
                "source": self.source,
            },
        )
        return Observation(**{**asdict(self), "request_id": request_id, "observation_id": oid})


@dataclass(frozen=True)
class RecommendationItem:
    blind_id: str
    observation_id: str
    similarity: float
    historical_request: str
    output_preview: str
    cost_usd: float
    latency_ms: float
    evidence_quality: float | None
    sample_age_days: float
    task_type: str


@dataclass(frozen=True)
class RecommendationSlate:
    slate_id: str
    query: str
    items: tuple[RecommendationItem, ...]
    created_at: float


@dataclass(frozen=True)
class Choice:
    slate_id: str
    blind_id: str
    buyer_id: str = "anonymous"
    created_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class Outcome:
    observation_id: str
    success: bool
    score: float | None = None
    buyer_id: str = "anonymous"
    created_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class SubsidyOffer:
    offer_id: str
    provider_id: str
    normal_price_usd: float
    subsidy_usd: float
    buyer_price_usd: float
    value_of_information: float
    reason: str
    expires_at: float
