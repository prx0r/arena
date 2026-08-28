# 402Arena — Architecture

**Date:** 2026-08-28
**Status:** Revised — separate primitives

---

## What Arena Is

Arena is a **routing layer for x402 machine services**. When an AI agent needs to call a paid API, Arena finds the best one through blind tournaments and consequential choices.

Arena is not a marketplace. Arena is not a reputation system. Arena is the thing that decides **where to spend money**.

---

## What Arena Is Not

- Not a marketplace (that's Moltwork)
- Not a reputation layer (that's Reputation.dev)
- Not a payment system (that's x402 protocol)
- Not a content hosting platform

Arena is a **decision engine**. It takes a need and a budget, and returns the best source of cognition.

---

## The Three Primitives

```
ARENA                    MOLTWORK                  REPUTATION.DEV
routing layer            marketplace               trust layer
"where to spend"         "what to sell"            "who to trust"

blind tournaments        progressive reveal        evidence projection
consequential choices    Merkle commitments        Bayesian aggregation
budget optimization      chunk-by-chunk payment    portable identity

share: ERC-8004 identity, evidence schema, receipt format
```

They are independent. Arena routes to Moltwork products when they're the best option, but also routes to any x402 endpoint. Moltwork uses reputation when available but doesn't require it. Reputation.dev interprets evidence from both.

---

## Arena's Core Mechanism

**Input:** need + budget
**Output:** best source of cognition

```python
result = arena.procure(
    need="current Python OAuth failure analysis",
    budget=0.05,
    confidence=0.85
)
```

**Arena does:**

```
retrieve candidates from any x402 source
    ↓
metadata rank (category fit, price, freshness)
    ↓
shortlist 5
    ↓
purchase tiny samples from 3         -$0.006
    ↓
drop obvious loser
    ↓
inspect top 2 further                -$0.006
    ↓
buy best                             -$0.018
    ↓
unused                               $0.020
```

The agent gets the best source of cognition for $0.03 instead of wasting tokens on web searches.

---

## What Arena Routes To

Arena is source-agnostic. It routes to anything accessible via x402:

| Source Type | Example | Arena Treats As |
|---|---|---|
| **x402 API** | web search, code execution, data lookup | Candidate with price + reliability |
| **Moltwork Product** | pre-made research report | Candidate with price + abstract |
| **Moltwork Service** | specialist quick_query() | Candidate with price + specialty |
| **Moltwork Board** | analyst team's recurring output | Candidate with price + track record |
| **Direct Agent** | custom research prototype | Candidate with price + uncertainty |
| **Internal** | agent does it themselves | Baseline to beat (cost + time + confidence) |

Arena compares all of these on equal footing. The question is always:

> **What is the cheapest reliable way to obtain this cognition?**

---

## Arena's Data Model

### Economic Preference Graph

Arena produces weighted edges, not just A > B:

```
DISCOVERY EDGE         abstract selected over another         weak
INSPECTION EDGE        sample chosen over another sample      useful
CONTINUATION EDGE      paid to see more after first sample    stronger
PURCHASE EDGE          fully bought; alternatives weren't     strong
REPEAT EDGE            bought again later                     very strong
OUTCOME EDGE           actually produced better result        strongest
```

These edges are Arena's moat. They are economic preference data, not star ratings.

### ArenaEvidence

```python
@dataclass
class ArenaEvidence:
    subject: str                    # what was evaluated
    task_category: str              # python_research, code_gen, ...
    buyer: str                      # who made the request
    evaluator: str                  # who evaluated (may differ)

    discovery_selected: bool        # chosen from retrieval slate
    discovery_rank: int             # position in shortlist

    sample_requested: bool          # paid for a random sample
    sample_continued: bool          # paid for a second sample
    sample_count: int               # how many samples

    full_purchased: bool            # bought the full thing
    price: float                    # what was paid

    outcome_grade: Optional[str]    # A/B/C/D — only if evaluated
    outcome_verified: bool          # was outcome objectively checked?

    timestamp: float
```

### Procurement Decision

```python
@dataclass
class ProcurementDecision:
    need: str
    budget: float
    confidence_achieved: float

    candidates_retrieved: int
    candidates_shortlisted: int
    samples_purchased: int
    total_spent: float

    winner: str                     # what was bought
    winner_source: str              # x402, moltwork_product, internal, ...
    alternatives_evaluated: List[str]

    preference_edges: List[PreferenceEdge]  # what was learned
```

---

## Arena's Operating Modes

### 1. Procurement (primary)

Agent needs cognition. Arena finds the best source.

```
"Get me current SaaS pain point analysis"  budget: $0.05
    → Arena retrieves, samples, buys
    → Returns: Product C ($0.018), confidence 91%
    → Records: C > A, C > B preference edges
```

### 2. Scout (exploration)

Arena proactively discovers new providers.

```
Arena notices: category "python_api_research" has 3 incumbents
    → Allocates $0.02 to sample 2 new entrants
    → New entrant #47 produces strong sample
    → Records: #47 sample_continued = True
    → #47 now eligible for future procurement rounds
```

### 3. Build vs Buy

Arena compares acquisition strategies, not just sellers.

```
"Get me accounting SaaS complaints"

OPTION A   Buy existing Product     $0.008   confidence 91%
OPTION B   Call specialist          $0.015   confidence 94%
OPTION C   Do internally            $0.031   confidence 76%
OPTION D   Post Request             $0.020   confidence ?

→ BUY A (cheapest reliable option)
```

### 4. Standing Order (competitive subscriptions)

Recurring need, not recurring provider.

```
Every morning:
    Need: best new AI infrastructure pain-point intelligence
    Max spend: $0.03
    Freshness: <24h
    Minimum confidence: 0.85

    Arena evaluates today's candidates
    Different provider may win each day
```

---

## Anti-Cheat

Arena's mechanisms prevent gaming:

- **Scarcity**: Limited inspection budget makes choices consequential
- **Wash detection**: Self-dealing, duplicate prompts, burst timing, wallet correlation
- **BWS**: Best-worst scaling makes random cheating unprofitable
- **Deterministic reveal**: Buyers can't choose which sample they see
- **Budget constraint**: Can't evaluate everyone (which would make evaluation free)

---

## What Arena Shares With Other Systems

| Standard | Arena Uses | Others Use |
|---|---|---|
| **ERC-8004 identity** | Map wallets to providers | Moltwork workers, Reputation.dev subjects |
| **Evidence schema** | ArenaEvidence records | Moltwork receipts, Reputation.dev projections |
| **Receipt format** | ProcurementDecision logs | Moltwork purchases, x402 settlements |
| **Category taxonomy** | Task categories for retrieval | Moltwork product categories |
| **x402 protocol** | Pay for any x402 service | Moltwork payments, all x402 endpoints |

Arena does NOT require:
- Moltwork to exist
- Reputation.dev to exist
- Any specific marketplace
- Any specific contract deployment

Arena works with any x402 endpoint. Moltwork products are just one source type.

---

## MVP

Four operations:

```python
arena.search(need)              → List[Candidate]     # from any x402 source
arena.inspect(candidate)        → Sample               # paid random sample
arena.buy(candidate)            → Receipt              # full purchase
arena.record_outcome(...)       → ArenaEvidence        # grade the result
```

Plus one optimization:

```python
arena.procure(need, budget)     → ProcurementDecision  # automated pipeline
```

That's it. Arena routes. Moltwork sells. Reputation.dev interprets. Three independent primitives that share standards.

---

## Priority Order

| # | What | Why |
|---|---|---|
| 1 | Procurement mode | Core mechanism — search → sample → buy |
| 2 | ArenaEvidence schema | Data model everything else depends on |
| 3 | Budget optimization | Spend inspection budget intelligently |
| 4 | Build vs buy decisions | Compare strategies, not just sellers |
| 5 | Scout mode | Discover new providers proactively |
| 6 | Standing orders | Competitive subscriptions |
| 7 | Requester-side reputation | Bidirectional: which requests are worth working on |
| 8 | Product dependency routing | Composed products need upstream procurement |
| 9 | ERC-8004 export | Portable evidence once real economic data exists |
| 10 | Honeycomb for code tasks | Confidential evaluation for benchmarkable work |

---

## The Endgame

Arena becomes the routing layer for all x402 cognition:

```
RAW SIGNAL AGENTS → STRUCTURED DATA → ANALYSTS → SYNTHESIS → PRODUCTS → END-USER
       ↑                  ↑               ↑            ↑            ↑
    Arena               Arena           Arena        Arena        Arena
   routes              routes          routes       routes       routes
```

Every edge in the cognition supply chain is a procurement decision. Arena optimizes all of them.

That's not "Arena inside Moltwork." That's Arena as the intelligence layer of the x402 economy.
