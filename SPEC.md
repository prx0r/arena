# 402Arena Spec v0.1 — The Cold-Start Arena

See README.md for vision. This spec defines the V1 primitives.

## Primitives

- `GET /recommend?q=<request>&budget=<usd>` — free, returns ranked endpoints with fit, price, evidence count. No wallet.
- `POST /choose/{id}` — records blind choice, reveals provider + payment route.
- `POST /outcome` — caller reports did-it-work (closes the loop for Hydra).
- `GET /research-credit?q=<request>` — does CG currently subsidize an exploratory provider for this request?

## Provider-Funded Exploration

Deposit → CG buys evidence on REAL user requests, not synthetic. Provider cannot buy ranking (hard rule). If API is bad, exploration scientifically establishes it.

## Active Learning

VOI = uncertainty × demand × novelty × competitive-uncertainty × freshness × routing-improvement / cost

if VOI > threshold: subsidize

Cogym evolves which acquisition policy builds the best router per dollar (5 policies → Hydra).

## Built On

- cogymkernel: deterministic worlds, content-addressed RunReceipts, hard gates
- HydraDB: shared evidence graph (REL_RAN_ON, blind-choice edges)
- x402 Bazaar: discovery (visibility) → 402Arena: credible discovery (quality)
