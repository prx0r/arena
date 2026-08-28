from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json


def evidence_hash(request_hash: str, response_hash: str, tx_hash: str | None, provider_id: str) -> str:
    raw = json.dumps({
        "request_hash": request_hash,
        "response_hash": response_hash,
        "tx_hash": tx_hash or "",
        "provider_id": provider_id,
    }, sort_keys=True, separators=(",", ":")).encode()
    return "0x" + sha256(raw).hexdigest()


@dataclass
class SimEscrow:
    """Deterministic mirror of ResearchEscrow.sol for simulation and property tests."""
    campaign_balance: dict[str, int] = field(default_factory=dict)
    provider_owner: dict[str, str] = field(default_factory=dict)
    paid_bounties: dict[str, int] = field(default_factory=dict)
    total_funded: int = 0
    total_paid: int = 0
    total_refunded: int = 0

    def fund(self, campaign_id: str, owner: str, amount_microusd: int) -> None:
        if amount_microusd <= 0:
            raise ValueError("amount")
        existing = self.provider_owner.get(campaign_id)
        if existing and existing != owner:
            raise PermissionError("campaign owner")
        self.provider_owner[campaign_id] = owner
        self.campaign_balance[campaign_id] = self.campaign_balance.get(campaign_id, 0) + amount_microusd
        self.total_funded += amount_microusd

    def pay(self, campaign_id: str, bounty_id: str, amount_microusd: int) -> None:
        if bounty_id in self.paid_bounties:
            raise ValueError("bounty replay")
        if amount_microusd <= 0 or self.campaign_balance.get(campaign_id, 0) < amount_microusd:
            raise ValueError("insufficient campaign balance")
        self.campaign_balance[campaign_id] -= amount_microusd
        self.paid_bounties[bounty_id] = amount_microusd
        self.total_paid += amount_microusd

    def refund(self, campaign_id: str, owner: str, amount_microusd: int) -> None:
        if self.provider_owner.get(campaign_id) != owner:
            raise PermissionError("campaign owner")
        if amount_microusd <= 0 or self.campaign_balance.get(campaign_id, 0) < amount_microusd:
            raise ValueError("amount")
        self.campaign_balance[campaign_id] -= amount_microusd
        self.total_refunded += amount_microusd

    def invariant(self) -> bool:
        return self.total_funded == self.total_paid + self.total_refunded + sum(self.campaign_balance.values())
