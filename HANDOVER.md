# HANDOVER — 2026-08-24 21:30 UTC

**Next agent: read this first. All other docs reference this.**

## What 402Arena Is

402Arena learns which machine service produces the best outcome for each kind of job. First vertical: **Research Arena** — routing search/research queries to the provider that wins for that query type.

> **Money buys experiments. Evidence buys organic ranking.** (`README.md:5`)

## Vertical Strategy (decided 2026-08-24)

| Vertical | Demand | Arena value | Status |
|----------|--------|-------------|--------|
| **Search / research** | Very high (Tavily 60K, Exa 11K calls) | Very high | **#1 — now** |
| **Deep reports / due diligence** | Medium | Very high | Layer 2 |
| **Images** | Low-medium | Extremely high | **#2** |
| Code generation | Likely useful | High | #3 |
| Video | Low today | Huge later | Later |
| Creative writing | Weak | Low | **No** (agents call LLMs directly) |

**Capability lineage added:** `capability_family`, `upstream_family`, `pipeline_fingerprint` fields on Provider/ProviderArm. Arena tracks upstream engines (tavily, exa, custom), not just URLs.

## Current Status

- **Tests:** 28/28 pass (mechanism, evidence_v1, evidence_market_v2, replay, ope, frontier, core)
- **Chain:** Base Sepolia 0x2bc8a74 (0 tx, dry-run)
- **Receipts:** 727+ total
- **Repo:** pushed to `prx0r/arena` at `7105faf`

## What Works (H1-H8)

| H | Hypothesis | Status | Evidence |
|---|---|---|---|
| H1 | Sponsor≠organic | CONFIRMED | `separated_ids beats paid_rank_bad` |
| H2 | Scarce 20% switch | CONFIRMED | `79.6% vs 100%` greedy +26pp |
| H3 | K=4 optimal | PROVISIONAL | `0.833 > 0.829` synthetic |
| H4 | BWS anti-cheat | CONFIRMED | delta 0.0017 |
| H5 | Wash detectable | CONFIRMED | 1.0 self-deal vs 0.0 clean |
| H6 | Lifecycle funds test | PROVISIONAL | not yet stressed |
| H7 | Hermes real | PARTIAL | 88% deterministic fallback |
| H8 | Market saturates | CONFIRMED | bid→0 at n>80 |

## Key experiment to prove this week

> Given one research query and three interchangeable x402 research/search providers, can Arena predict which output a blind evaluator will prefer better than cheapest/default/random routing?

That's the killer experiment. If it works, 402Arena becomes an **empirical routing layer for agent intelligence**.

## Remaining gaps (top 5)

1. Wire record_tournament into daemon (not just record_best_worst)
2. Enforce 2-reveal limit
3. Wire adaptive_k to live uncertainty (not iter_n %4)
4. Integrate bounty.py with x402 USDC on Base Sepolia
5. Deploy escrow contract on Base Sepolia

## Key Commands

```bash
# Run tests
cd /root/arena && python3 -m pytest -q

# Run simulation
PYTHONPATH=. python scripts/run_mechanism_sweep.py --rounds 1200 --seeds 12
```
