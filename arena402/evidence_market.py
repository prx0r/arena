from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import math
import secrets
import time
from collections import defaultdict

from .mechanism import Bounty, EvidenceGrade, EvidenceQuote, stable_hash


@dataclass(frozen=True)
class EvidenceMarketConfig:
    max_organic_bid_usd: float = 0.01
    max_research_reward_usd: float = 0.02
    min_bid_usd: float = 0.00005
    quote_ttl_s: int = 300
    bounty_ttl_s: int = 900
    saturation_mass: float = 60.0
    duplicate_discount: float = 0.05
    freshness_half_life_days: float = 21.0


class CoverageBook:
    def __init__(self):
        self.mass: dict[tuple[str, str], float] = defaultdict(float)
        self.last_seen: dict[tuple[str, str], float] = {}
        self.demand: dict[str, float] = defaultdict(float)

    def observe_demand(self, task: str, weight: float = 1.0) -> None:
        self.demand[task] += max(0.0, weight)

    def add_evidence(self, task: str, provider_id: str, *, weight: float = 1.0, created_at: float | None = None) -> None:
        k = (task, provider_id)
        self.mass[k] += max(0.0, weight)
        self.last_seen[k] = created_at or time.time()

    def coverage(self, task: str, provider_id: str) -> float:
        return self.mass[(task, provider_id)]


class EvidenceMarket:
    """Live bid curve for machine experience.

    Prices are driven by expected value of information, not a fixed reward.
    Organic evidence is cheaper than commissioned evidence because Arena did not
    have to pay for the underlying call.
    """

    def __init__(self, coverage: CoverageBook, uncertainty_fn, cfg: EvidenceMarketConfig | None = None):
        self.coverage = coverage
        self.uncertainty_fn = uncertainty_fn
        self.cfg = cfg or EvidenceMarketConfig()
        self.seen_receipts: set[str] = set()
        self.seen_payload_pairs: set[tuple[str, str]] = set()

    def _freshness_need(self, task: str, provider_id: str, now: float) -> float:
        last = self.coverage.last_seen.get((task, provider_id))
        if not last:
            return 1.0
        age_days = max(0.0, (now - last) / 86400)
        return 1.0 - 0.5 ** (age_days / self.cfg.freshness_half_life_days)

    def value_score(self, task: str, provider_id: str, *, evidence_strength: float = 1.0, future_transfer: float = 1.0) -> tuple[float, tuple[str, ...]]:
        now = time.time()
        mass = self.coverage.coverage(task, provider_id)
        saturation = 1.0 / math.sqrt(1.0 + mass / max(self.cfg.saturation_mass, 1e-9))
        unc = min(1.0, max(0.0, float(self.uncertainty_fn(task, provider_id))))
        demand_mass = self.coverage.demand.get(task, 0.0)
        demand = 0.15 if demand_mass <= 0 else min(1.0, math.log1p(demand_mass) / math.log(500.0))
        fresh = self._freshness_need(task, provider_id, now)
        score = min(1.0, evidence_strength * future_transfer * (0.38 * unc + 0.27 * saturation + 0.22 * demand + 0.13 * fresh))
        reasons = []
        if unc > 0.6: reasons.append("high-routing-uncertainty")
        if saturation > 0.7: reasons.append("coverage-gap")
        if demand > 0.6: reasons.append("high-future-demand")
        if fresh > 0.6: reasons.append("stale-evidence")
        if not reasons: reasons.append("marginal-evidence")
        return score, tuple(reasons)

    def quote_organic(self, task: str, provider_id: str, *, grade: EvidenceGrade,
                      request_hash: str, response_hash: str, receipt_hash: str | None) -> EvidenceQuote:
        dup = (request_hash, response_hash) in self.seen_payload_pairs or (receipt_hash is not None and receipt_hash in self.seen_receipts)
        grade_strength = {
            EvidenceGrade.A_PROVIDER_BOUND: 1.00,
            EvidenceGrade.B_ARENA_OBSERVED: 0.90,
            EvidenceGrade.C_BUYER_ATTESTED: 0.45,
            EvidenceGrade.D_UNVERIFIED: 0.10,
        }[grade]
        value, reasons = self.value_score(task, provider_id, evidence_strength=grade_strength)
        bid = self.cfg.max_organic_bid_usd * (value ** 1.7)
        if dup:
            bid *= self.cfg.duplicate_discount
            reasons = tuple(reasons) + ("duplicate-discount",)
        if bid < self.cfg.min_bid_usd:
            bid = 0.0
        now = time.time()
        return EvidenceQuote(
            quote_id=stable_hash("quote", {"task":task,"provider":provider_id,"now":int(now // 30),"request":request_hash,"response":response_hash}),
            evidence_kind="organic-x402-trace",
            bid_usd=round(bid, 8),
            expires_at=now + self.cfg.quote_ttl_s,
            reasons=reasons,
            required_grade=EvidenceGrade.C_BUYER_ATTESTED if bid < 0.001 else EvidenceGrade.B_ARENA_OBSERVED,
        )

    def issue_bounty(self, *, request_id: str, task: str, provider_id: str, provider_cost_usd: float,
                     campaign_id: str | None = None, required_grade: EvidenceGrade = EvidenceGrade.B_ARENA_OBSERVED) -> Bounty | None:
        value, _ = self.value_score(task, provider_id, evidence_strength=1.0)
        if value < 0.20:
            return None
        reward = min(self.cfg.max_research_reward_usd, max(self.cfg.min_bid_usd, value * 0.01))
        now = time.time()
        nonce = secrets.token_hex(16)
        return Bounty(
            bounty_id=stable_hash("bounty", {"request":request_id,"provider":provider_id,"nonce":nonce}),
            request_id=request_id,
            provider_id=provider_id,
            max_provider_cost_usd=provider_cost_usd * 1.05,
            reimbursement_usd=provider_cost_usd,
            research_reward_usd=round(reward, 8),
            deadline=now + self.cfg.bounty_ttl_s,
            nonce=nonce,
            required_grade=required_grade,
            campaign_id=campaign_id,
        )

    def accept_evidence(self, *, task: str, provider_id: str, grade: EvidenceGrade,
                        request_hash: str, response_hash: str, receipt_hash: str | None, weight: float) -> None:
        self.seen_payload_pairs.add((request_hash, response_hash))
        if receipt_hash:
            self.seen_receipts.add(receipt_hash)
        strength = {
            EvidenceGrade.A_PROVIDER_BOUND: 1.0,
            EvidenceGrade.B_ARENA_OBSERVED: 0.9,
            EvidenceGrade.C_BUYER_ATTESTED: 0.55,
            EvidenceGrade.D_UNVERIFIED: 0.15,
        }[grade]
        self.coverage.add_evidence(task, provider_id, weight=max(0.0, weight) * strength)
