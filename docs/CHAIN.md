# Chain choice — 402Arena

**Decision: simulate chain-agnostic, prototype on Base Sepolia, deploy on Base mainnet. ETH L1 only if we need L1 security for EAS attestations (still bridgeable).**

Why not ETH mainnet now:
- x402 V2 + facilitator + Bazaar are Base-native; gas $0.001 vs $1-5 on ETH kills micro-bounties ($0.003 jobs)
- 402Arena bounties need cheap settlement for `arena-evidence-v1` receipts (requestHash+responseHash)
- Mechanically, chain only matters for `providerSignature` + `txHash` binding; simulation should test incentives without paying gas

What we build now (mechanisms):
- `simulation/agent_rank_sim.py` — 5 archetypes × 33 styles proxy, scarce 2-reveals vs full reveal, logs `logs/rank_sim_{scarce,full}.jsonl` (250 each, 452K total)
- `arena402/bounty.py:issue_challenge` — signed `arena_task_id` before purchase, verifiable `requestHash`
- `arena402/report.py` — experimental provider dashboard (not ad dashboard)

Prototype on Base Sepolia:
- Deploy `arena-evidence-v1` receipt verifier as EAS attestation on Base Sepolia (cheap, EAS exists on Base)
- Use `402arena-cg` proxy x402 flow with `facilitator` on Base Sepolia
- Keep `provider_funds` ledger off-chain (DB) until chain needed; on-chain only for bounty escrow + attestations

When to add ETH:
- If we need Ethereum Attestation Service on ETH mainnet for cross-ecosystem claims
- Bridge attestations Base → ETH via EAS offchain → on-chain

Next: evolve `K, VoI, subsidy` thresholds via Cogym on `logs/*.jsonl` → Hydra `REL_RAN_ON` → next recipe; then point bounties at Base Sepolia.
