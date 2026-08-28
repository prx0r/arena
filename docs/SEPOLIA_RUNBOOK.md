# Base Sepolia runbook

## Network

Base Sepolia:

- chain ID `84532`;
- CAIP-2 `eip155:84532`;
- public RPC `https://sepolia.base.org` (rate-limited; use a production provider later);
- Circle test USDC `0x036CbD53842c5426634e7929541eC2318f3dCF7e`.

Official Base faucet documentation lists CDP and third-party faucets for test ETH. Circle/CDP can supply test USDC. Testnet tokens have no monetary value.

## Roles

Use separate keys even on testnet:

- `BUYER` — pays x402 endpoint;
- `SELLER_PAYMENT_ADDRESS` — receives payment;
- `SELLER_SIGNING_PRIVATE_KEY` — signs x402 offer/receipt and Arena evidence; should differ from payee;
- `ARENA_OPERATOR` — authorizes research bounty payout;
- `PROVIDER_CAMPAIGN_OWNER` — deposits campaign budget.

## Witness

1. start `chain-ts/src/seller.ts`;
2. buyer sends unpaid POST and receives 402;
3. x402 client creates EVM exact payment on Base Sepolia and retries;
4. seller returns 200 + official x402 settlement/receipt evidence;
5. seller response contains `arenaEvidence` binding request and core response SHA-256 hashes;
6. buyer verifies signature/hash and writes `arena-evidence.json`.

## Research escrow

`ResearchEscrow` stores only campaign balances and payout commitments. Bounty event includes `evidenceHash`; full evidence is offchain.

USDC has 6 decimals, so `$0.001` = 1,000 atomic units.

## Batch anchoring

At end of test run:

```bash
python scripts/make_evidence_root.py evidence.jsonl
```

Call `EvidenceRootRegistry.anchor(batchId, root, count)` and independently recompute the root before considering the batch verified.
