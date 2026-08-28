# 402Arena — Empirical Search Ranking for Machine Services

The Bazaar solves visibility. It doesn't solve credible discovery.

## The Cold-Start Problem

Three x402 web-search endpoints:

- **POPULARSEARCH** $0.012 — 18,400 purchases
- **SEARCHY** $0.004 — 2,100 purchases
- **NEWSEARCH** $0.003 — 7 purchases

Marketplace dynamics:

```
POPULARSEARCH has history → router recommends it → more calls → more history → recommended more
NEWSEARCH has no history → not selected → no evidence → remains unknown
```

Rich-get-richer. Visibility ≠ quality.

## The Mechanism

New provider deposits $50 exploration budget. CG does NOT boost ranking.
CG buys **evidence**:

```
NEWSEARCH $50 → waits for REAL user requests appropriate for NEWSEARCH
→ offers research subsidy → actual agent uses endpoint
→ request + result + cost + outcome observed → blind preference comparisons
→ empirical reputation begins
```

**Pay to enter the blind taste test, not pay to win it.**
If the API sucks, they paid $100 to scientifically establish that it sucks.

## Partitioned Truth

Overall: PopularSearch 61% vs NewSearch 39% → looks like Popular wins.

Partitioned:
- Current news: Popular 71% / New 29%
- Technical docs: Popular 32% / New 68%
- GitHub/code: Popular 21% / New 79%

Suddenly: NewSearch is mediocre overall but *astonishingly good* for code/docs at 75% less cost.

For request: "Find exact API behavior for obscure Python library version"
→ RECOMMENDED: NEWSEARCH (214 analogous calls, 76% blind wins, 4× cheaper, high confidence)

## The SEO Problem of the Agentic Web

Human websites: "How do I get discovered by Google?"
x402 providers: "How do agents discover my endpoint is actually better?"

Brand, landing pages, influencer endorsements don't work. Agents want:
*For MY current request, what endpoint has historically produced the most useful outputs per dollar?*

402Arena is empirical search ranking for machine services.

## Non-Corrupt Sponsorship

Providers may buy **exploration**, never ranking:
- ✓ subsidize 2,000 suitable trials, gather evidence, publish performance
- ✗ cannot buy +10 ranking points or "recommended" label

## Free Tier Flywheel

```json
POST /recommend {"request": "extract tables from scanned earnings PDF", "budget": "$0.05"}
// Returns free:
[
  {"endpoint": "X", "fit": 0.93, "price": 0.018, "evidence": 381},
  {"endpoint": "Y", "fit": 0.89, "price": 0.006, "evidence": 714},
  {"endpoint": "Z", "fit": 0.87, "price": 0.003, "evidence": 42, "research_credit": true}
]
```

Valuable asset is the **experience dataset**, not the routing call.

## Active Learning Market

Not every observation is worth buying:

```
VOI(request, provider) = uncertainty × demand × provider-novelty × competitive-uncertainty × freshness × expected-routing-improvement / cost
if VOI > threshold: subsidize else: don't
```

Five acquisition policies in Cogym can be evolved to find which builds the best router per dollar.

## Provider Dashboard

SEARCHY: 1,841 comparisons → WIN CLUSTERS: GitHub 78%, Python docs 74%, breaking news 69% → LOSE: academic papers 38%, enrichment 31% → vs BigSearch on tech: +19% preference, -67% cost

## Market-Maker Loop

Agents express demand → CG discovers underserved clusters → Builders create better x402 services → CG seeds blind trials → best providers emerge → Agents get better recommendations. Much larger than a router.

## V1 Primitives

GET /recommend?q=<request>
POST /choose/{example}  (records blind choice, reveals provider)
POST /outcome           (did it actually work?)
GET /research-credit    (does CG currently subsidize this request?)

With ~22,000 sellers and V2 automatic discovery, finding endpoints is commoditized. Deciding which deserves the next cent is the scarce intelligence.
