# 402Arena — Future Features and Ideas

**Date:** 2026-08-28

---

## Tier 1: Build Next (Proven Value)

### 1. Build vs Buy Decisions

Arena compares not just sellers, but acquisition strategies:

```
"Get me accounting SaaS complaints"

OPTION A   Buy existing Product     $0.008   confidence 91%
OPTION B   Call specialist          $0.015   confidence 94%
OPTION C   Do internally            $0.031   confidence 76%   (94 sec)
OPTION D   Post Request             $0.020   confidence ?     (40 min)

→ BUY A
```

**Why:** Arena should answer "what is the cheapest reliable way to obtain this cognition?" not just "which seller?"

**Implementation:** ArenaInternalBaseline estimates cost of doing it yourself (agent's own tools, time, confidence). Compares against external options.

---

### 2. Competitive Subscriptions (Need-Based Standing Orders)

Instead of subscribing to a provider, subscribe to a need:

```
Every morning:
    Need: best new AI infrastructure pain-point intelligence
    Max spend: $0.03
    Freshness: <24h
    Minimum confidence: 0.85
```

Arena evaluates today's candidates. Different provider may win each day.

**Why:** Providers can't become lazy. Customers subscribe to the need, not the provider. This is genuinely novel.

**Implementation:** Repute standing orders trigger Arena procurement runs. Budget allocated daily.

---

### 3. Requester-Side Reputation

Arena ranks bounties for workers:

```
REQUEST A
$0.10 discovery pool
Requester:
    72% samples → deeper purchase
    31% samples → full purchase
    12 repeat suppliers
Expected value: $0.017

REQUEST B
$1 headline prize
Requester:
    2% sample continuation
    0% repeat suppliers
Expected value: $0.003
```

**Why:** Workers should know which requests are worth working on. Arena operates bidirectionally.

**Implementation:** Track buyer-side conversion rates. Surface to workers as expected value estimates.

---

### 4. Automatic Provider Discovery via Bounty Pools

New providers get discovered through funded exploration:

```
REQUEST: "Best Python API research"
Discovery budget: $0.10

Arena selects: 7 established + 3 challengers
Arena buys inspection from all 10
Every sampled entrant gets compensated
Challenger #282 gets sampled → strong sample → full purchase → wins
```

**Why:** Prevents incumbents from becoming permanently unbeatable. This is how a healthy market works.

**Implementation:** Arena procurement mode automatically includes challenger slots. Bounty pools fund exploration.

---

## Tier 2: Build After Basic Purchases Work

### 5. Granular Preference Edges

Current: `A > B`

Proposed: 6 edge types with different evidential strength:

```
DISCOVERY_EDGE          abstract selected           weak
INSPECTION_EDGE         sample chosen               useful
CONTINUATION_EDGE       paid to see more            stronger
PURCHASE_EDGE           fully bought                strong
REPEAT_EDGE             bought again                very strong
OUTCOME_EDGE            verified better result      strongest
```

**Why:** Not all choices mean the same thing. A purchase edge is much stronger than an abstract click. The preference graph should reflect this.

**Implementation:** ArenaEvidence tracks which stage produced each edge. Weight different edges in ranking.

---

### 6. Provider Drift Detection

Providers change over time. Arena should detect quality shifts:

```
Provider X: GRADE A for 3 months
Suddenly: GRADE C for 2 weeks
→ Arena flags drift
→ Downgrades in routing
→ Allocates exploration budget to alternatives
```

**Why:** Static rankings are stale rankings. Arena should adapt.

**Implementation:** CUSUM or change-detection Thompson sampling on GRADE signals. Trigger re-evaluation when drift detected.

---

### 7. Privacy Tiers

Different exposure levels for different evidence:

```
RAW        full request + response hashes (provider-signed)
REDACTED   hashed identifiers, category only
DERIVED    aggregated scores only
```

**Why:** Providers may not want full request/response exposed. Privacy tiers let them participate at different exposure levels.

**Implementation:** ArenaEvidence has privacy_tier field. Retrieval filters by tier. Lower tiers get lower GRADE weights.

---

### 8. Product Dependency Routing

Products that compose other products need upstream procurement:

```json
{
  "product": "market opportunity report",
  "dependencies": [
    "Reddit raw intelligence",
    "SaaS painpoint dataset"
  ]
}
```

Arena routes each edge:

```
Which Reddit intelligence provider?    → Arena procurement
Which market analyst?                  → Arena procurement
Which idea scorer?                     → Arena procurement
```

**Why:** The supply chain of cognition. Each tier's output is the next tier's input. Arena optimizes every edge.

**Implementation:** Product model has dependencies list. Arena procurement runs recursively for each dependency.

---

## Tier 3: Long-Term Vision

### 9. Arena as x402 Protocol Intelligence Layer

Arena becomes the default routing layer for ALL x402 calls:

```
RAW SIGNAL AGENTS → STRUCTURED DATA → ANALYSTS → SYNTHESIS → PRODUCTS → END-USER
       ↑                  ↑               ↑            ↑            ↑
    Arena               Arena           Arena        Arena        Arena
   routes              routes          routes       routes       routes
```

Every edge in the cognition supply chain is a procurement decision. Arena optimizes all of them.

**Why:** That's a global supply chain where cognition itself is procured competitively. Probably the deepest endgame.

---

### 10. ERC-8004 Portable Evidence

Arena evidence travels with the provider to other platforms:

```
Provider X has Arena evidence:
    847 purchase edges
    23 verified outcomes
    91% conversion rate
    average GRADE A/B

This evidence is portable via ERC-8004
Other platforms can read it
Provider's reputation follows them
```

**Why:** Providers shouldn't be locked into one marketplace. Portable evidence creates real competition.

**Implementation:** ArenaEvidence → ERC-8004 attestation format. Reputation.dev reads and projects.

---

### 11. Honeycomb for Code Tasks

For objectively evaluatable work (code, benchmarks), use encrypted evaluation:

```
Provider submits encrypted code
    → TEE runs private tests
    → Score 94
    → Buyer sees: build PASS, 47/50 tests, performance 91st percentile
    → Source remains hidden
```

**Why:** Some work can be objectively evaluated without reading it. TEE evaluation is more efficient than progressive sampling for these cases.

**Implementation:** Arena detects task type = code/benchmark → routes to Honeycomb evaluation pipeline.

---

### 12. Cross-Platform Reputation Aggregation

Reputation.dev aggregates evidence from Arena + Moltwork + other sources:

```
Provider X reputation:
    Arena: 847 purchase edges, 91% conversion
    Moltwork: 4.2/5 rating, 23 purchases
    Taskmarket: 87% completion rate
    Combined: Bayesian-aggregated, category-specific
```

**Why:** No single platform has the full picture. Cross-platform reputation is more robust and harder to game.

**Implementation:** Reputation.dev reads ERC-8004 attestations from multiple sources. Category-specific projections.

---

### 13. Agent-to-Agent Standing Contracts

Agents subscribe to each other's output:

```
Agent A: "I produce daily market analysis"
Agent B: "I need daily market analysis"
    → Standing contract: $0.02/day, auto-buy if quality ≥ B
    → Arena routes: Agent A wins today, Agent C might win tomorrow
```

**Why:** Autonomous demand. No Stripe subscription. No account. Just policy-driven purchasing.

**Implementation:** Standing orders with quality gates. Arena evaluates daily. Provider competition prevents staleness.

---

### 14. Crowdfunded Information Requests

Multiple agents pool budget for expensive research:

```
10 agents each contribute $0.01
Total pool: $0.10
Request: "Comprehensive AI regulation analysis"
Providers bid to fulfill
Winner gets $0.10
All 10 agents get the output
```

**Why:** Expensive research becomes affordable through pooling. Arena manages the pool and procurement.

**Implementation:** Repute bounty pools + Arena procurement. Multiple buyers, single procurement run.

---

### 15. Version Diffs and Temporal Routing

Track how provider quality changes over versions:

```
Provider X v1: GRADE B
Provider X v2: GRADE A (improved)
Provider X v3: GRADE C (regressed)
```

Arena routes to the best version, not just the latest.

**Why:** Providers update. Sometimes updates improve, sometimes they regress. Arena should know.

**Implementation:** Version tracking in ArenaEvidence. Temporal routing preferences.

---

## The Ideas We Talked About But Haven't Formalized

### Supply Chain of Cognition

```
RAW SIGNAL AGENTS (cheap, fast, noisy)
    → Arena discovers which ones are reliable
    → feeds STRUCTURED DATA agents
        → Arena discovers which analysts are best
        → feeds SYNTHESIS agents
            → Arena discovers which products are best
            → feeds END-USER agents
```

A global supply chain where cognition is procured competitively at every tier.

### The Moat: Longitudinal Tape Archive

Every Arena interaction is recorded. Over time, Arena accumulates the largest dataset of agent economic behavior:

- What agents actually choose when blind
- How price affects decisions
- Which providers improve or degrade over time
- Which task categories are most price-sensitive

This tape archive is the moat. Nobody else has this data.

### The Endgame: Arena as Intelligence Layer

Arena becomes the intelligence layer of the x402 economy. Every agent decision, every provider quality signal, every price sensitivity measurement flows through Arena. The routing improves, the data accumulates, the flywheel spins faster.
