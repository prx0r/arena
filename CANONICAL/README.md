# 402Arena — Canonical Reference

**Created:** 2026-08-28
**Status:** Complete audit and reference

---

## Files

| # | File | What It Is |
|---|---|---|
| 00 | [AUDIT](00-AUDIT.md) | Full project audit: codebase, experiments, hypothesis status |
| 01 | [ARCHITECTURE](01-ARCHITECTURE.md) | How it all ties together: data flow, layers, moat |
| 02 | [MECHANISMS](02-MECHANISMS.md) | Best mechanisms and why they work (10 mechanisms) |
| 03 | [COMPETING](03-COMPETING.md) | Competing mechanisms and why Arena is different |
| 04 | [DATA-PIPELINE](04-DATA-PIPELINE.md) | How data flows end to end, bootstrapping problem |
| 05 | [FUTURE](05-FUTURE.md) | Sick future features and ideas (15 ideas) |
| 06 | [TODOS](06-TODOS.md) | 5 things to do, in order |

---

## Quick Reference

**What Arena is:** Routing layer for x402 machine services. "What's the best x402 for this function, based on actual agent choices?"

**What Arena is not:** Marketplace, reputation system, payment system, content platform.

**Core mechanism:** Blind tournament → consequential choice → economic preference graph → evidence → reputation.

**Key invariant:** Money buys experiments. Evidence buys organic ranking. Nobody pays for position.

**The moat:** Economic preference graph — weighted edges from actual purchasing behavior. Nobody else has this data.

**The flywheel:** More agents → more choices → better routing → more agents.

**5 TODOs:**
1. Real provider catalog (20+ endpoints)
2. Fix LLM gateway (real choices)
3. Procurement mode (automated pipeline)
4. ArenaEvidence + edge types
5. Base Sepolia deployment
