# 402Arena — Architecture

**Date:** 2026-08-28
**Status:** Revised — blind taste test for AI work

---

## What Arena Is

Arena is the **blind taste test for AI work**. Humans pick their favourite output from multiple providers. Arena accumulates genuine quality signals. Agents route based on what humans actually think is good, not metadata.

Core rule: **Human preference is the only anti-slop mechanism that works.**

---

## What Arena Is Not

- Not a router (that's RouteNet, Agent402)
- Not a payment layer (that's x402, MPP)
- Not a marketplace (that's Moltwork, Agent402)
- Not a directory (that's CDP Bazaar, SwarmBazaar)

Arena is a **quality intelligence layer**. It knows what's actually good because humans said so.

---

## The Problem Arena Solves

The x402 ecosystem has 15,000+ endpoints. Most agents pick by:
- Price (cheapest wins)
- Uptime (is it online?)
- Metadata (what does the docs say?)

None of that tells you **what the output is actually like.**

Two providers can both return "research results" for the same query. One gives you 5 relevant articles with good analysis. The other gives you 5 random links with a ChatGPT summary. Same price. Same uptime. Completely different quality.

**Arena is the only way to know the difference.**

---

## How Arena Works

```
Human needs: "Research report on AI regulation in the EU"

Arena shows (blind):
  A  [research report from Provider X]     $0.08
  B  [research report from Provider Y]     $0.12
  C  [research report from Provider Z]     $0.05

Human reads all 3.
Picks B as best.
Arena records: B > A, B > C

Next human asks the same question:
Arena already knows B is best for EU research.
Recommends B with confidence.
```

---

## The Subjective Sweet Spot

Arena matters for work where quality varies and humans can tell the difference:

| Category | Example | Why Arena Matters |
|---|---|---|
| **Research reports** | "Analyze AI regulation landscape" | Depth, accuracy, insight vary 10x |
| **Writing / copywriting** | "Write a blog post about X" | Style, clarity, voice vary |
| **Code review** | "Review this contract for vulnerabilities" | Thoroughness varies dramatically |
| **Data analysis** | "Find trends in this dataset" | Insight quality varies |
| **Summarization** | "Summarize this paper" | What's included/excluded matters |
| **Legal / compliance** | "Summarize these regulations" | Accuracy matters, wrong = expensive |
| **Financial analysis** | "Analyze this company's position" | Wrong = expensive |
| **Design critique** | "Evaluate this design" | Taste matters |

Arena does NOT matter for:

| Category | Example | Why Arena Doesn't Matter |
|---|---|---|
| UUID generation | "Generate a UUID" | All providers identical |
| Currency conversion | "USD to EUR" | All providers identical |
| Gas price lookup | "What's the gas price?" | All providers identical |
| Geocoding | "Address to lat/lng" | All providers identical |
| Simple web search | "Search for X" | Quality difference minimal |

---

## Why Human Choices Are Non-Slop Intel

Agent choices are:
- Algorithmic (similarity scores, price comparison)
- Fast (millisecond decisions)
- Shallow (metadata-based)
- **Gameable** (optimize for the algorithm)

Human choices are:
- **Genuine** (actually read the output)
- **Subjective** (style, depth, accuracy)
- **Consequential** (they care about the result)
- **Hard to game** (you can't optimize for a blind test)
- **Transferable** (one human's preference informs others)

**Non-slop intel = data that can't be faked, gamed, or synthesized.**

When a human reads 3 research reports and picks the best one, that's a real quality signal. No algorithm produced it. No metadata predicted it. No synthetic data approximated it. A person with taste said "this one is better."

That's the moat.

---

## The Evidence Graph

Each human choice produces weighted edges:

```
DISCOVERY     Human saw 5 options
CHOICE        Human picked B
QUALITY       Human rated B: 4.5/5
COMPARISON    B > A, B > C (from the same session)
CATEGORY      "EU research" (task type)
PRICE         B cost $0.08, A cost $0.05, C cost $0.12
TIMESTAMP     when the evaluation happened
EVALUATOR     who chose (human identity, not anonymous)
```

Over time, Arena accumulates category-specific quality intelligence:

```
For "EU research":
  Provider B: wins 73% of comparisons, avg 4.3/5, $0.08
  Provider A: wins 18% of comparisons, avg 3.8/5, $0.05
  Provider C: wins 9% of comparisons, avg 3.2/5, $0.12

Recommendation:
  "For EU research, Provider B is best value.
   Provider A is cheaper but lower quality.
   Provider C is overpriced for what you get.
   Confidence: high (47 human evaluations)"
```

---

## How To Get the Data

### Method 1: Humans Choose Naturally

Arena is an MCP tool:

```python
result = arena.compare(
    task="Write a research report on EU AI regulation",
    providers=["exa", "tavily", "custom"],
    budget=0.15
)
```

Arena:
1. Calls 3 providers with the same query
2. Stores all outputs
3. Shows them blind to the human
4. Human picks favourite
5. Arena records the preference

**Humans do this because they need to choose a provider anyway.** Arena makes the choice easier and captures the data.

### Method 2: Funded Evaluation

```
Arena posts:
"Evaluate 3 research reports on AI regulation.
 Pick the best one.
 We'll pay you $0.50 for your time."

10 humans evaluate → 30 preference edges
Cost: $5.00
```

### Method 3: Provider-Funded Testing

```
Provider B says:
"I'm better than A and C for research.
 Fund a comparison test to prove it."

Arena runs blind test with 20 humans.
Result: B wins 78%.
Provider B gets: verified quality badge.
```

---

## The Revenue Model

### Free: Humans Evaluating

Humans get better recommendations by choosing blind. They don't pay. They generate the data.

### Paid: Providers Want Intelligence

```
"How do I compare to competitors?"
  → Arena shows: "You win 73% for EU research, but only 41% for US tech"

"Where am I losing?"
  → Arena shows: "You lose on depth. Your reports are shorter than competitors."

"What should I improve?"
  → Arena shows: "Add more citations. Winners average 12 sources, you average 4."
```

**Providers pay for quality intelligence.** Not for routing. For knowing where they stand.

### Paid: Agents Want Quality Routing

```
Agent: "For this research task, which provider is actually best?"
Arena: "Provider B wins 73% of human comparisons for this task type.
        Confidence: high (47 evaluations).
        Cost: $0.08."
Agent: "Send it."
```

**Agents pay $0.003 for Arena's recommendation to save $0.20 on a bad call.**

---

## The MCP Server

Arena as an MCP server. Any agent can call it.

```python
# Compare providers blind
result = arena.compare(task="...", providers=[...], budget=0.15)

# Get quality recommendation
rec = arena.recommend(task="...", category="research")

# Record a human choice
arena.record_choice(session_id="...", chosen="B", ratings={"A":3, "B":5, "C":2})

# Get provider quality report
report = arena.provider_report(provider_id="...", category="research")
```

---

## What Arena Shares

| Standard | Arena Uses |
|---|---|
| **x402** | Pay for provider calls |
| **ERC-8004** | Provider identity |
| **MCP** | Agent integration |
| **ArenaEvidence** | Quality records |

Arena does NOT require Moltwork, Reputation.dev, or any specific marketplace.

---

## The Moat

Arena's moat is the **human preference graph** — weighted edges from actual humans reading actual outputs and picking their favourites.

Nobody else has this data. RouteNet knows if a provider is online. Agent402 knows what it costs. Arena knows **what it's actually like.**

The more humans evaluate, the better Arena's recommendations become. That's the flywheel.

---

## Priority Order

| # | What | Why |
|---|---|---|
| 1 | MCP server | Distribution to every agent |
| 2 | Blind comparison tool | Core mechanism — show outputs, human picks |
| 3 | Index top 50 quality-varying endpoints | Not all 15,000, just the ones where quality varies |
| 4 | Human evaluation pipeline | Get real preference data |
| 5 | Provider quality reports | Revenue model — providers pay for intelligence |
| 6 | Category-specific routing | "For EU research, Provider B wins" |
| 7 | Standing comparisons | "Compare these 3 providers for my ongoing needs" |
| 8 | Evidence graph visualization | Show providers their competitive position |

---

## The One-Liner

> **Arena is the blind taste test for AI work. Humans pick their favourite. Providers learn where they stand. Agents route based on what humans actually think is good.**

Non-slop intel. That's the product.
