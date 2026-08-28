# Simulation Design — Full x402 + Hermes Integration

**Goal:** replicate x402 actual schemas, use Hermes as customer/worker agents, exemplar provider paying $5, data they get back, whole algorithm presenting outputs to Hermes and which they pick — integrated into `simulation.py` (12-provider hidden winner) + `chain-ts`.

## 1. x402 Schemas Replicated (from verbatims + spec)

**x402 v2 core** (`chain-ts` `@x402/fetch` `@x402/evm`):
- `402 Payment Required` response with `resource` URL, `accepts: [{scheme:"exact", network:"eip155:84532", maxAmountRequired:"3000", payTo:"0xSeller", asset:"0x036CbD USDC"}]`
- `facilitator: https://x402.org/facilitator` verifies payment, returns `X-PAYMENT` header
- `Signed Offers & Receipts` extension: provider signs `offer` pre-payment, `receipt` post-payment proves `resource, payer, amount, txHash, timestamp` but **not** `request/response body` (`402molt:340`).

**Arena Evidence v1** (`arena-provider-evidence-v1`):
- `requestHash = sha256(request_body)`, `responseHash = sha256(response_body)`, `providerSignature = sign(resource+requestHash+responseHash)` (`402molt:378`)
- Grades: `A provider-bound 1.0 / B arena-observed 0.90 / C buyer-attested 0.55 / D unverified 0.15` (`mechanism.py:28`)

**On-chain:** `Base Sepolia 84532` `USDC 0x036CbD` `ResearchEscrow.sol` (budgets + replay-protected payouts) + `EvidenceRootRegistry.sol` Merkle roots (`README.md:160`).

**Simulation replicates** all off-chain: `x402.py` `resource/pay/receipt/offer` structs with `requestHash/responseHash` binding, no real USDC.

## 2. Hermes as Exemplary Agents

**Customer Agent (Buyer):** has `query + budget + wallet`, calls `arena.recommend` → receives `5 blind` (provider+price hidden) → spends `2 reveals` (`arena40254:60`) → `BEST/WORST` (BWS) → `price reveal` → `ACTUAL PURCHASE` (x402 pay) → `outcome` → receipt. **Payoff:** gets provider reveal + `research subsidy -$0.006` if experimental slot (`arena40254:202`).

**Worker Agent (Bounty):** `arena.work()` → `BOUNTY: call NewSearch with challenge #71982 cost $0.003 reimburse $0.003 reward $0.002` (`arena40254:590`) → `arena_task_id + requestHash + nonce + deadline + max_price` (`bounty.py:13` issued before purchase) → makes x402 call with `providerSignature` → `request→provider→output→tx→evidence` → `Arena verifies` → `provider graph seeded`.

**Worker Agent (Scout):** `ARENA SCOUT TASK` `evaluate 5 blind outputs → full ordering + best/worst + reason_codes $0.0016` (`arena40254:720`) with hidden controls `deterministic tasks/repeated pairs` and `reliability posterior Beta (s+2)/(t+4)` (`anti_cheat.py:22`).

All via `hermes -z ox-alpha → mimo` `HERMES_AGENT_SPEC.md:7` each `kanban claim` is one agent query.

## 3. Exemplar Provider Paying Us

**NewSearch deposits `$5` research budget** (`store.provider_funds`):

```
Provider UI: "Fund $5 to prove Search402 deserves traffic"
  ↓
ResearchEscrow (off-chain mirror ledger.py for sim, on-chain USDC for Sepolia)
  ↓
Arena exposure: `ExposureWeight = relevance × uncertainty × info × log1p(budget)` (`arena40254:466`) diminishing, `Trial1 $0.005 → $0.50 paused` after 50 losses (`exploration.py:73`)
```

**Data they get back** (`provider_report.py` 22 rows `arena40254:1001`):

```
NEWSEARCH — ARENA CAMPAIGN
Budget $5 deposited $1.20 spent
Qualified opportunities 2,419
Blind appearances 611 avg relevance 0.91
Blind first-choice 184/611 30.1% / top-2 53.7%
Purchase after reveal 28.3% vs first 30.1% (price effect -1.8pp)
Task clusters: technical docs 61%→58% vs news 18%→11%
Competitors: vs BigSearch 71% win, SearchPro 54%, Cheap 38%
Niche: technical docs +23% vs market -71% price
Spend per discovery $0.04 etc
+ request cluster, opponents, propensity, blind result, reveal, purchase, outcome
RAW (opt-in) / REDACTED / DERIVED embedding+taxonomy (arena40254:369)
```

**Value:** where they have product-market fit, not just good.

## 4. Whole Algorithm Presenting Outputs to Hermes

```
REQUEST q
  ↓
HARD ELIGIBILITY (sim≥thr AND schema/budget/health) (MECHANISM_SPEC.md:10)
  ↓
CANDIDATE POOL
  ↓
┌─────────────┴─────────────┐
ORGANIC VALUE              RESEARCH VALUE (VoI)
E[utility] cost/latency    Demand×Uncertainty×Novelty×Drift×CompProb (402arena:497)
  ↓                          ↓
exploit pool               explore pool (funded NewSearch)
  └───────────┬─────────────┘
              ↓
       SAFE SLATE OPTIMIZER (relevance, diversity MMR, regret ≥0.95 organic, adaptive K=3-6)
              ↓
        RANDOMIZED BLIND ORDER (position shuffle, p_include/p_position logged store.py:49)
              ↓
         HERMES CHOOSES: 5 blind → keep 2 → reveal first → buy? → reveal second (arena40254:108 sequential)
         BEST/WORST (BWS) → price reveal → ACTUAL PURCHASE
              ↓
        downstream outcome (success 0.85 vs 0.7) + x402 receipt + arena-evidence-v1
              ↓
        store.record_best_worst + record_tournament + outcomes → wash_score → Hydra REL_RAN_ON → Cogym evolves K/thr/VoI
              ↓
        Provider dashboard + Merkle batch → EvidenceRootRegistry (chain-ts)
```

**Integration into `simulation.py`:** deterministic 12-provider market already has hidden cheap niche winner; add `control` provider 10%, inject `NewSearch $5` via `sponsor.py`, run `hermes -z` customer/worker loops as above, log `logs/integrated_sim.jsonl` + `HERMES_AGENT_SPEC.md` receipts.

