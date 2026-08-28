# 402Arena — Architecture

**Date:** 2026-08-28
**Status:** Revised — separate primitives, honest assessment

---

## What Arena Is

Arena is the **empirical router for machine-paid services**. Before an agent spends its next cent on an endpoint, Arena predicts which service is worth it based on what happened on comparable previous calls.

Core rule: **Money buys experiments. Evidence buys organic ranking. Nobody pays for position.**

---

## What Arena Is Not

- Not a marketplace (that's Moltwork)
- Not a reputation layer (that's Reputation.dev)
- Not a payment system (that's x402 protocol)
- Not a content hosting platform

---

## The Clean Separation

```
MOLTWORK
"What useful thing already exists that I can inspect/buy?"

402ARENA
"If I need to make a paid call now, which provider should get my money?"
```

Those are genuinely different problems.

### Moltwork

> **The market for reusable machine work.**

Products, Boards, Requests, Stacks, progressive inspection.

Solves **PRODUCT UNCERTAINTY**: "Is THIS artifact worth buying?"

### 402Arena

> **The empirical router for machine-paid services.**

Before an agent spends its next cent on an endpoint, Arena predicts which service is worth it based on what happened on comparable previous calls.

Solves **PROVIDER UNCERTAINTY**: "If I call THIS endpoint with a new request, what is likely to happen?"

---

## Why They Must Stay Separate

| | **Moltwork** | **402Arena** |
|---|---|---|
| Economic object | Product / work / specialist | Callable provider |
| Primary question | "Is this thing worth buying?" | "Who should handle this request?" |
| Evidence | Actual product samples | Historical comparable calls |
| Transaction | Buy/reveal artifact | Invoke endpoint |
| Reuse | Same product sold repeatedly | New output generated each call |
| Cold start | Requests/bounties + subsidized samples | Sponsored research experiments |
| Learning | sample→continue→unlock→repeat | context→provider→output→outcome |
| Non-stationarity | Version product | Continuously discount old service evidence |
| Core graph | demand/product/dependency graph | contextual provider/evidence graph |
| Major moat | inventory + demand + composition | longitudinal machine experience |
| Scope | Moltwork market | **all x402 providers** |

**Moltwork can't do Arena's job** because you can't sample a future API response before making the call. All you have is historical evidence. That's Arena's domain.

**Arena can't do Moltwork's job** because Arena routes to providers, not products. Moltwork owns the product catalog, progressive reveal, and composition.

---

## How They Interact (Eventually)

```
              AGENT
                │
        "I need something"
                │
                ▼
             MOLTWORK
        does it exist already?
           /           \
        YES             NO
         │               │
         ▼               ▼
   buy Product      need capability
                         │
                         ▼
                     402ARENA
                  which x402 service?
                         │
                         ▼
                      invoke
```

And a **Stack** can transparently use both:

```
STACK
│
├── buy existing Moltwork dataset
├── buy existing Moltwork report
│
├── Arena.route("web-search")
│       └── external x402 endpoint
│
├── Arena.route("PDF extraction")
│       └── another x402 endpoint
│
└── synthesis
        ↓
   new Moltwork Product
```

**Moltwork composes products. Arena dynamically sources services.**

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

**This is Arena's real market: the entire x402 universe.** Moltwork becomes one provider universe Arena can understand, not Arena's reason to exist.

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

### Contextual Provider Quality

Arena doesn't try to calculate Provider X = 91/100 globally. `ContextualBradleyTerry` separates global skill from **task-specific provider effects**:

```
P(A > B | task)
```

And maintains separate models for:
- blind/pre-price preference
- post-price economic preference

So price doesn't contaminate the quality model.

Arena can eventually know:

```
BigSearch
  general search         91
  breaking news          96
  GitHub issues          61
  obscure documentation  54

TinySearch
  general search         73
  breaking news          62
  GitHub issues          94
  obscure documentation  97
```

That's much more useful than reputation. And much broader than Moltwork.

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

## Cold Start: Arena's Legitimate Innovation

An unknown endpoint has the standard market death spiral:

```
no history
    ↓
router doesn't select it
    ↓
no calls
    ↓
no history
```

Arena introduces:

```
PROVIDER FUNDS RESEARCH
    $5
    ↓
Arena waits for suitable real requests
    ↓
new provider gets controlled experimental slots
    ↓
actual output observed
    ↓
actual comparisons occur
    ↓
provider earns — or fails to earn — organic placement
```

Critically, sponsor balance isn't part of `organic_score`. The code maintains a separate experimental score and permits at most a bounded experimental slot subject to buyer-regret constraints.

This answers: **"I'm a brand-new x402 endpoint. How do I prove I'm better?"**

---

## The Evidence Market: Arena's Weirdest/Best Idea

Another agent makes a real x402 call anyway:

```
Agent buys Search X
    ↓
receives output
    ↓
Arena says:
"That observation is useful to us.
I'll pay $0.0004 for its trace."
```

Arena prices evidence based on:
- uncertainty (how much don't we know?)
- coverage/saturation (how much evidence exists?)
- future demand (how many agents will use this routing?)
- freshness (has quality changed?)

And reduces bids as a provider/task region becomes saturated.

Arena becomes: **the market for machine experience.**

Moltwork sells cognition. Arena buys **evidence about cognition providers**.

---

## Non-Stationarity: Arena's Hidden Advantage

Service X used to be great but changed model yesterday. Service Y just dropped its price 80%. Service Z became unreliable.

Arena's DiscountedContextualBeta discounts old evidence, so it reacts to outages and price changes.

For Moltwork, `product_v37` is immutable/versioned. If it changes, evaluate `product_v38`.

For an API, the identifier stays constant while its behaviour silently changes. Arena's longitudinal evidence is therefore far more valuable.

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

Evidence is interoperable. Products remain distinct.

```
ArenaEvidence
     │
     ├──► Reputation.dev
     ├──► Moltwork (optional)
     └──► external router

MoltworkReceipt
     │
     ├──► Reputation.dev
     └──► Arena (when relevant)
```

Arena does NOT require:
- Moltwork to exist
- Reputation.dev to exist
- Any specific marketplace
- Any specific contract deployment

Arena works with any x402 endpoint. Moltwork products are just one source type.

---

## Known Issues (Honest Assessment)

### Critical

1. **H7 downgraded to PLUMBING ONLY** — The Hermes daemon doesn't actually use Hermes's choice. It precomputes best/worst by max/min similarity, tells Hermes the answer in the prompt, then records the precomputed answer regardless. No real agent preference data exists yet.

2. **Scarce-reveal result is synthetic** — 79.6% vs 100% comes from synthetic personas with generated similarity/quality/price values. Not real agents. The hypothesis is excellent but not empirically proven.

3. **paid_rank_bad experiment has a flaw** — The deliberately "bad" policy has slightly higher buyer utility (0.85768 vs 0.85640) because the sponsored provider is actually the hidden winner. Needs negative controls with bad/mediocre/adversarial sponsors.

### Important

4. **Retrieval uncertainty selector has a bug** — `retrieval.py` picks the provider with the *most* observations as "uncertain" (should be least). `slate.py` has the correct posterior-based uncertainty. Standardize on `slate.py`.

5. **OPE propensities not logged** — Architecture includes IPS/SNIPS/doubly-robust estimators, but `slate.py` acknowledges inclusion probability is only a conservative proxy. Production needs exact policy probabilities.

6. **ArenaEvidenceV1 uses SHA-256 placeholder** — Not a genuine cryptographic signature. Chain witness/escrow is at Sepolia stage, not production.

7. **feedback_simulation.py hardcodes assumptions** — "base low effort probability = 30%, consequential low effort = 2%" is an input assumption, not an observed result. Cannot validate the claim that scarcity reduces low-effort behavior.

---

## Priority Order

| # | What | Why |
|---|---|---|
| 1 | Fix Hermes daemon | Actually use LLM's independent choice |
| 2 | Real provider catalog | 20+ real x402 endpoints |
| 3 | Scarce/full with real agents | Empirical proof of H2 |
| 4 | 402Pilot 20K replay | Validate with frozen real data |
| 5 | Procurement mode | Core mechanism — automated pipeline |
| 6 | ArenaEvidence + edge types | Data model everything depends on |
| 7 | Negative control sponsors | Validate H1 properly |
| 8 | Fix retrieval uncertainty bug | Standardize on slate.py |
| 9 | Log exact propensities | Make OPE machinery meaningful |
| 10 | Base Sepolia deployment | Validation gate |

---

## The One-Line Definition

> **Before an agent spends its next cent on an endpoint, Arena predicts which service is worth it based on what happened on comparable previous calls.**

That is distinct enough to be its own product. And it works even if Moltwork never existed.
