# HANDOVER — 2026-08-24 22:00 UTC

**Next agent: read this first. All other docs reference this.**

## What 402Arena Is

Arena for non-fungible machine outputs. Where different providers produce materially different outputs, quality is hard to pre-judge, and choosing well matters.

> **Don't Arena commodities. Arena outputs where taste/quality matters.**

## Thesis (refined 2026-08-24)

Arena is valuable when three conditions hold simultaneously:
1. Different providers produce **materially different outputs**
2. Quality is **difficult to know before buying**
3. The output costs enough that **choosing well matters**

This disqualifies search (too fungible after LLM synthesis), RPC, price feeds, raw LLM access. It points to images, deep research, video, specialized analysis, generated artifacts.

## Verticals

| Vertical | Different outputs? | Hard to pre-judge? | Arena fit | Status |
|----------|-------------------|--------------------|-----------|--------|
| **Images** | massively | yes | excellent | **#1 — cleanest demo** |
| **Deep research reports** | yes | yes | excellent | **#2** |
| Video | yes | yes | excellent (expensive) | later |
| Specialized analysis | yes | yes | excellent | #3 |
| Code | varies | often testable | medium | #4 |
| Web search | somewhat | low | weak | routing only |
| Creative writing | no | no | none | — |

## Current Status

- **Tests:** 28/28 pass
- **Chain:** Base Sepolia (0 tx, dry-run)
- **Repo:** `prx0r/arena` at `06f0bcc`

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

> Given one image generation request and three different x402 image providers, can Arena predict which output a blind evaluator will prefer better than cheapest/random routing?

That's the killer experiment. Images are the cleanest demo: metadata cannot tell you which image you'll prefer. You have to see the outputs.

If it works, 402Arena becomes the **empirical routing layer for non-fungible machine outputs**.

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
