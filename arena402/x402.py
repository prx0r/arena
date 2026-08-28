from __future__ import annotations

"""Thin x402 boundary.

402Arena deliberately keeps payment execution outside the ranking model. The
router can reveal a direct endpoint or a proxy can implement this protocol.
"""

from dataclasses import dataclass
from typing import Protocol, Any
import hashlib
import time


@dataclass(frozen=True)
class Quote:
    provider_id: str
    endpoint: str
    price_usd: float
    network: str = "eip155:84532"  # Base Sepolia
    payment_requirements: dict[str, Any] | None = None


@dataclass(frozen=True)
class X402Resource:
    url: str
    method: str = "POST"
    accepts: tuple[dict[str, Any], ...] = ()


@dataclass(frozen=True)
class X402Payment:
    resource: str
    payTo: str
    maxAmountRequired: str  # e.g. "3000" = $0.003 USDC 6 decimals
    asset: str = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"  # Base Sepolia USDC
    network: str = "eip155:84532"
    payer: str = "0xBuyer"


@dataclass(frozen=True)
class X402Receipt:
    resource: str
    payer: str
    payTo: str
    amount: str
    network: str
    txHash: str
    timestamp: int
    facilitator: str = "https://x402.org/facilitator"


@dataclass(frozen=True)
class X402Offer:
    resource: str
    payTo: str
    maxAmountRequired: str
    asset: str
    network: str
    signature: str  # provider-signed
    expiresAt: int


@dataclass(frozen=True)
class ArenaEvidenceV1:
    """arena-provider-evidence-v1 binds request/response hashes (x402 receipt does not) per 402molt:378"""
    resource: str
    payer: str
    provider: str
    requestHash: str  # sha256(request_body)
    responseHash: str  # sha256(response_body)
    amount: str
    network: str
    txHash: str
    issuedAt: int
    providerSignature: str

    @staticmethod
    def create(resource: str, payer: str, provider: str, request_body: str, response_body: str, amount: str, txHash: str) -> "ArenaEvidenceV1":
        rh = hashlib.sha256(request_body.encode()).hexdigest()
        rph = hashlib.sha256(response_body.encode()).hexdigest()
        sig = hashlib.sha256(f"{resource}:{rh}:{rph}:{provider}".encode()).hexdigest()  # placeholder ed25519
        return ArenaEvidenceV1(resource, payer, provider, rh, rph, amount, "eip155:84532", txHash, int(time.time()), sig)


class X402Executor(Protocol):
    def quote(self, endpoint: str, payload: dict | None = None) -> Quote: ...
    def purchase(self, quote: Quote, payload: dict | None = None) -> dict: ...


class DryRunExecutor:
    """Safe default: never spends; useful for local tests and hackathon demos."""
    def quote(self, endpoint: str, payload: dict | None = None) -> Quote:
        return Quote(provider_id="unknown", endpoint=endpoint, price_usd=0.0)
    def purchase(self, quote: Quote, payload: dict | None = None) -> dict:
        raise RuntimeError("DryRunExecutor never purchases. Configure a real x402 executor explicitly.")
