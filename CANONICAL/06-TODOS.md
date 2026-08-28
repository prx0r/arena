# 402Arena — 5 TODOs

**Date:** 2026-08-28

---

## TODO 1: Real Provider Catalog (This Week)

**Problem:** Arena has 2 providers in simulation. Real routing needs 20+ real x402 endpoints.

**What to do:**
1. Index the x402 ecosystem — scrape Bazaar, check x402.org, register our own endpoints
2. Create `arena402/providers.json` with real metadata:
   ```json
   [
     {"id": "x402egoic_redirect", "name": "Redirect Analyzer", "price": 0.002, "category": "web_analysis", "endpoint": "https://x402.egoic.ai/redirect"},
     {"id": "x402egoic_domain", "name": "Domain Lookup", "price": 0.003, "category": "web_analysis", "endpoint": "https://x402.egoic.ai/domain"},
     {"id": "noslop_detect", "name": "AI Text Detection", "price": 0.003, "category": "content_analysis", "endpoint": "https://noslop.egoic.ai/detect"},
     ...
   ]
   ```
3. Build a simple provider registration flow — providers self-register with metadata
4. Index at least 20 real endpoints before doing live experiments

**Why first:** Everything else depends on having real things to route to.

**Done when:** `arena402 providers.json` has 20+ real x402 endpoints with metadata.

---

## TODO 2: Fix LLM Gateway for Real Choices (This Week)

**Problem:** ox-alpha-free flaky. 75% deterministic fallback. No real agent preferences.

**What to do:**
1. Fix the `hermes -z` prompt to require JSON output:
   ```python
   prompt = f"""You are evaluating x402 service providers.

   Candidates:
   {slate_json}

   Pick the BEST and WORST. Return JSON:
   {{"best": "blind_id", "worst": "blind_id", "reason": "brief explanation"}}"""
   ```
2. Use `--json` flag if available
3. Switch primary to mimo-v2.5 (works reliably) as primary, ox-alpha as experimental
4. Run 100+ real iterations and measure: what % are real LLM choices vs deterministic fallback?

**Why second:** Real choices are the fuel. Without them, Arena is a well-engineered engine with no gas.

**Done when:** >50% of daemon iterations produce real LLM choices (not deterministic fallback).

---

## TODO 3: Build Procurement Mode (Next Week)

**Problem:** Arena can rank but can't automatically procure. Agents still have to manually browse slates.

**What to do:**
1. Implement `arena.procure(need, budget)`:
   ```python
   def procure(self, need: str, budget: float, confidence: float = 0.85) -> ProcurementDecision:
       # 1. Retrieve candidates
       candidates = self.search(need, k=10)
       
       # 2. Shortlist by metadata
       shortlist = self.metadata_rank(candidates, k=5)
       
       # 3. Sample top 3
       for candidate in shortlist[:3]:
           sample = self.inspect(candidate, budget=min(0.003, budget))
           budget -= sample.cost
           if sample.quality < threshold:
               shortlist.remove(candidate)
       
       # 4. Inspect top 2 further
       for candidate in shortlist[:2]:
           deeper = self.inspect(candidate, budget=min(0.005, budget))
           budget -= deeper.cost
       
       # 5. Buy best
       winner = shortlist[0]
       self.buy(winner, budget=budget)
       
       return ProcurementDecision(...)
   ```
2. Add build-vs-buy comparison (internal baseline vs external options)
3. Test with synthetic data, then live

**Why third:** This is the killer feature. Arena becomes a cognition procurement optimizer, not just a router.

**Done when:** `arena.procure("Python OAuth analysis", 0.05)` returns a bought result with leftover budget.

---

## TODO 4: ArenaEvidence Schema + Edge Types (Next Week)

**Problem:** Current preference edges are just `A > B`. No granularity. No provenance.

**What to do:**
1. Implement ArenaEvidence dataclass:
   ```python
   @dataclass
   class ArenaEvidence:
       subject: str
       task_category: str
       buyer: str
       evaluator: str
       
       discovery_selected: bool
       discovery_rank: int
       
       sample_requested: bool
       sample_continued: bool
       sample_count: int
       
       full_purchased: bool
       price: float
       
       outcome_grade: Optional[str]
       outcome_verified: bool
       
       timestamp: float
   ```
2. Implement 6 edge types with weights:
   ```python
   EDGE_WEIGHTS = {
       "discovery": 0.2,
       "inspection": 0.4,
       "continuation": 0.6,
       "purchase": 0.8,
       "repeat": 0.9,
       "outcome": 1.0,
   }
   ```
3. Record edges during tournament flow
4. Store in SQLite alongside existing tables
5. Update ranking to use weighted edges

**Why fourth:** The preference graph is Arena's moat. Making it granular makes it much more valuable.

**Done when:** Every Arena interaction produces typed, weighted preference edges with full provenance.

---

## TODO 5: Deploy on Base Sepolia + Live Test (2 Weeks)

**Problem:** Arena is simulation-only. No real money flowing. No on-chain evidence.

**What to do:**
1. Deploy ResearchEscrow.sol on Base Sepolia:
   ```bash
   cd contracts && forge script Deploy.s.sol --rpc-url https://base-sepolia.g.alchemy.com/v2/{key} --broadcast
   ```
2. Deploy EvidenceRootRegistry.sol
3. Fund test wallets with testnet USDC (0x036CbD53842c5426634e7929541eC2318f3dCF7e)
4. Wire Arena procurement to use real USDC:
   - Agent requests procurement
   - Arena samples and buys via escrow
   - Receipts are Merkle-rooted on-chain
   - Evidence is verifiable
5. Run 50 live procurement cycles on testnet
6. Measure: conversion rates, preference edges, wash scores

**Why fifth:** This proves Arena works with real money, not just simulation. It's the validation gate before mainnet.

**Done when:** 50 live procurement cycles on Base Sepolia with real USDC, on-chain evidence roots, verifiable receipts.

---

## The 5 TODOs in Order

| # | What | When | Blocks |
|---|---|---|---|
| 1 | Real provider catalog (20+ endpoints) | This week | Everything |
| 2 | Fix LLM gateway (real choices) | This week | Live experiments |
| 3 | Procurement mode (automated pipeline) | Next week | Agent adoption |
| 4 | ArenaEvidence + edge types | Next week | Moat formation |
| 5 | Base Sepolia deployment | 2 weeks | Validation gate |

**After these 5:** Standing orders, requester reputation, product dependencies, ERC-8004 export, Honeycomb integration.
