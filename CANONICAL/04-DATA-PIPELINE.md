# 402Arena — Data Pipeline: How Data Flows End to End

**Date:** 2026-08-28

---

## The Problem

Arena needs data to work. Real data. Not synthetic. The question: where does it come from?

---

## Data Sources (What We Have)

### 1. Synthetic Simulation (L0)

**File:** `arena402/simulation.py`

**What:** 12-provider deterministic market with hidden cold-start winner.

**Providers:**
- `incumbent` $0.010 — coding 0.84, research 0.86, extraction 0.81, fresh-search 0.91
- `mid` $0.003 — balanced mid-tier
- `cheap` $0.0007 — low quality everywhere
- `flaky` $0.002 — good quality, 25% failure rate
- `extractor` $0.002 — excellent at extraction (0.94), bad at everything else
- `fast` $0.002 — low latency (210ms), decent quality
- `academic` $0.006 — best at research (0.92), slow (1200ms)
- `news` $0.004 — best at fresh-search (0.95)
- `structured` $0.003 — best at extraction (0.90)
- `general` $0.003 — mediocre at everything
- `budget` $0.0004 — cheapest, worst quality
- `newseed` $0.0012 — hidden winner for coding (0.92) and research (0.89), cheap ($50 sponsor budget)

**What it proves:** Arena can discover `newseed` (hidden cold-start winner) that organic-only never finds. K=4 optimal. Separated_ids beats corruption.

**Limitation:** Synthetic. No real agents, no real prices, no real quality variation.

### 2. 402Pilot Frozen Responses

**File:** `scripts/fetch_402pilot.py`, `arena402/datasets.py`

**What:** 823 tasks × 5 providers × 5 response variants = 20,575 frozen responses.

**Providers:** P-cheap, P-mid, P-premium, P-adv, P-flaky
**Tasks:** HumanEval (code), HotpotQA (research), TriviaQA (extraction), OpenWeb (fresh-search)

**How to get:**
```bash
python scripts/fetch_402pilot.py --out /tmp/402Pilot
python scripts/import_402pilot_store.py --repo /tmp/402Pilot
```

**What it proves:** Arena can replay frozen responses and measure routing quality. Scripts exist but haven't been run at scale yet (20K replay).

**Limitation:** Static snapshot. Providers don't change. No economic behavior (just quality scores).

### 3. Live Hermes Daemon

**File:** `scripts/continuous_hermes_daemon.py`

**What:** Real LLM calls via `hermes -z ox-alpha-free` → fallback `mimo-v2.5` → deterministic.

**How it works:**
1. Claims tasks from Hermes kanban board (`cogym-lab`)
2. Creates ephemeral SQLite Store with 2 providers
3. Runs EvidenceRetriever.search() with K cycling 3,4,5,6
4. Calls hermes -z for blind choice
5. Records best_worst, wash_score, writes JSONL receipt

**What it proves:** Plumbing works. Hermes is actually called. Provenance logged. Wash clean.

**Limitation:** ox-alpha flaky. 75% deterministic fallback. Not real agent preferences.

### 4. Agent Ranking Simulation

**File:** `simulation/agent_rank_sim.py`

**What:** 5 archetypes (greedy, cautious, anxious, reckless, analytical) × 50 queries, scarce vs full reveal.

**What it proves:** Scarcity creates consequential choice. 20.4% switch after price reveal.

**Limitation:** Synthetic archetypes, not real agents.

---

## Data Sources (What We Need)

### 5. Real x402 Endpoints

**What:** A catalog of 20+ real x402 services with metadata.

**We have:**
- `x402fun/` — 4 endpoints (redirect, domain, cors, dmarc) at `x402.egoic.ai`
- `noslop/` — AI text detection endpoint

**We need:**
- Web search x402 APIs
- Code execution x402 APIs
- Data lookup x402 APIs
- Research x402 APIs
- Translation x402 APIs
- Image generation x402 APIs
- Any x402 endpoint listed in Bazaar

**How to get:** Index the x402 ecosystem. Scrape Bazaar. Register our own endpoints. Invite providers.

### 6. Real Agent Choices

**What:** Agents actually calling Arena and making procurement decisions.

**We have:** 727 receipts, but 75% deterministic fallback.

**We need:** Agents with working LLM gateways making real blind choices on real queries.

**How to get:** Fix ox-alpha prompt. Use mimo-v2.5 as primary. Deploy Arena as MCP server. Get agent frameworks to use it.

### 7. Real Economic Behavior

**What:** Agents spending real money on inspections and purchases.

**We have:** Simulation shows 20.4% switch after price reveal.

**We need:** Real USDC (or testnet USDC) flowing through Arena.

**How to get:** Deploy on Base Sepolia. Fund test wallets. Let agents spend.

### 8. Provider Quality Data

**What:** Ground truth on provider quality for validation.

**We have:** Synthetic quality scores in simulation.

**We need:** Real outcomes from real x402 calls. Did the code execute? Did the research answer the question? Did the data match reality?

**How to get:** Outcome recording. Buyer calls POST /outcome. Arena grades quality.

---

## The Bootstrapping Problem

Arena needs data to route well. But agents won't use Arena until it routes well.

**Solution: Seed with what we have.**

```
Phase 1: Synthetic data
  - Simulation proves mechanism works
  - 12 providers, 4 tasks, 5 archetypes
  - K=4 optimal, separated_ids beats corruption

Phase 2: Frozen replay
  - 402Pilot 20K responses
  - Replay with different policies
  - Measure: which policy discovers hidden winners fastest?

Phase 3: Live daemon
  - Hermes makes real calls
  - ox-alpha flaky, but deterministic fallback works
  - Proves plumbing, not preferences

Phase 4: Real x402 endpoints
  - Index 20+ real endpoints
  - Real agents making real choices
  - Real USDC flowing

Phase 5: Flywheel
  - More data → better routing → more agents → more data
```

---

## Data Pipeline Architecture

```
SOURCE                  INGESTION              STORAGE              OUTPUT
─────────────────────────────────────────────────────────────────────────
x402 endpoints     →    metadata scraping  →   providers table  →   catalog
402Pilot frozen    →    fetch + normalize  →   observations    →   replay corpus
Hermes daemon      →    -z calls           →   slates + choices →   live receipts
Agent queries      →    retrieval search   →   similarity vecs  →   routing
Provider funds     →    CampaignBook       →   sponsor_balance  →   exploration budget
Evidence market    →    quote_organic()    →   CoverageBook     →   bid curve
Anti-cheat         →    AntiCheat.score()  →   wash_scores      →   fraud flags
```

---

## What the Data Actually Looks Like

### JSONL Receipt (Live)

```json
{
  "slate_id": "slate_a1b2c3d4",
  "query": "Python OAuth failure analysis",
  "items": [
    {"blind_id": "x1", "observation_id": "obs_123", "similarity": 0.892, "cost_usd": 0.003},
    {"blind_id": "x2", "observation_id": "obs_456", "similarity": 0.847, "cost_usd": 0.008},
    ...
  ],
  "choice": {"finalists": ["x1", "x3"], "reveal_order": ["x3", "x1"], "bought": "x3"},
  "wash_score": 0.0,
  "k": 4,
  "model": "ox-alpha-free",
  "timestamp": 1693200000
}
```

### ArenaEvidence (Proposed)

```json
{
  "subject": "provider_x",
  "task_category": "python_research",
  "buyer": "agent_abc",
  "evaluator": "agent_abc",
  "discovery_selected": true,
  "discovery_rank": 1,
  "sample_requested": true,
  "sample_continued": true,
  "sample_count": 2,
  "full_purchased": true,
  "price": 0.008,
  "outcome_grade": "A",
  "outcome_verified": false,
  "timestamp": 1693200000
}
```

### Preference Edge (Proposed)

```json
{
  "source": "provider_x",
  "target": "provider_y",
  "edge_type": "purchase",
  "weight": 1.0,
  "task_category": "python_research",
  "price_source": 0.008,
  "price_target": 0.012,
  "buyer": "agent_abc",
  "timestamp": 1693200000
}
```
