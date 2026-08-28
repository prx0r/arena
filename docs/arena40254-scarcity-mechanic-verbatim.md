Yes. The mechanism gets much better if we stop thinking:

> “How do we persuade an agent to fill out a survey?”

and instead design the interaction so **the agent’s own desire to discover/buy the right provider produces the preference data automatically**.

The provider-funded bounty system then becomes a second, separate way of generating evidence.

## The critical distinction

There should be three kinds of Arena interaction:

| Mode              | Agent's goal                      | What Arena learns                            | Who pays?      |
| ----------------- | --------------------------------- | -------------------------------------------- | -------------- |
| **Buyer**         | Find something useful to purchase | genuine revealed preferences                 | free           |
| **Scout**         | Evaluate alternatives             | deeper ranking/preference data               | Arena          |
| **Bounty worker** | Earn money running experiments    | authenticated request→provider→output traces | Arena/provider |

Do **not** ask ordinary buyers for a seven-item full ranking. The deeper you ask them to rank, the less consequential the answers become.

There is real choice-modeling evidence for this problem: best/worst and ranking can extract more statistical information than asking only for a first choice, but the preferences inferred from deeper choices can differ from the first-choice utility, and later choices can be less consistent. ([PubMed Central (PMC)][1])

So I'd make **organic buyer feedback consequential**, while paying separately for deeper scientific evaluation.

# The buyer mechanic I'd use

Suppose the agent asks:

> Find me an x402 that can research obscure Python API documentation.

Arena finds five historical outputs relevant to that intent.

We show:

```text
BLIND ARENA

A  [historical output]
B  [historical output]
C  [historical output]
D  [historical output]
E  [historical output]

Providers hidden.
Prices hidden.
```

But don't say:

> rank 1–5 and we'll show everything.

Because:

```text
random ranking
→ all information unlocked
```

is a perfectly rational cheap strategy.

Instead give the agent **two reveal credits**.

> “Which two would you actually want to investigate?”

That choice matters.

If it chooses:

```text
C
A
```

we reveal only:

```text
C = NewSearch
current price: $0.003

A = BigSearch
current price: $0.019
```

Now we have a strong preference:

```text
C,A > B,D,E
```

and some weaker ordering:

```text
C > A
```

depending on whether we asked them sequentially.

The agent had to actually look at the outputs because wasting one of its two reveals on garbage hurts **it**.

That's much stronger anti-cheat than saying:

> “Please rank honestly.”

---

# Make it sequential and we get even more

I'd actually implement this:

```text
5 blind examples
       ↓
"Which one would you inspect first?"
       ↓
C
       ↓
reveal C provider + price
       ↓
Buy C?
   │
   ├── YES → done
   │
   └── NO
        ↓
"Which remaining answer would
you inspect next?"
        ↓
A
        ↓
reveal A + price
        ↓
...
```

Now every reveal produces another point in a **partial ranking**:

```text
C > A > remaining alternatives
```

but only insofar as the buyer actually needed to keep searching.

That is exactly the kind of data we want.

An agent that immediately buys C gives us:

```text
C was first blind choice
C survived price reveal
C was actually purchased
```

Very strong.

An agent that chooses C blind but rejects it after discovering `$0.08`, then buys A at `$0.004`, gives us two separate things:

```text
QUALITY PREFERENCE
C > A

ECONOMIC PREFERENCE
A > C at observed prices
```

That distinction is extremely valuable.

# We should probably NOT reveal every provider for free

This is the key to maintaining incentive compatibility.

The thing Arena possesses isn't just recommendations.

It possesses:

> **the mapping between impressive historical evidence and the service that created it.**

That's valuable information.

So the basic free service could be:

```text
Query     FREE
5 blind evidence cards

First reveal     FREE
Second reveal    FREE

Further reveals:
tiny payment
OR Arena research credit
OR deeper feedback
```

Not because we're trying to charge agents meaningful money.

Because **reveal scarcity makes their choices consequential**.

Even `$0.0001` per additional reveal could be enough to make random clicking irrational for autonomous agents optimizing spend.

---

# Even better: use subsidies as the reward

Suppose Arena particularly wants evidence about NewSearch.

It appeared as candidate D.

Don't tell the buyer this.

Buyer ranks:

```text
1 C
2 D
```

Only after commitment:

```text
C = BigSearch
$0.012

D = NewSearch
$0.007

ARENA RESEARCH CREDIT
-$0.006

effective cost:
$0.001
```

Now Arena exploration gives the buyer something it actually values.

And because **the ranking was committed before prices/providers/subsidies were revealed**, sponsorship cannot contaminate the blind preference.

That's an extremely nice mechanism.

---

# A provider's $1,000 should buy measurement, but in a very measurable way

I think you're correct that saying:

> “You lost 60/100”

is nearly useless to a new provider.

They should receive a research dashboard more like:

```text
NEWSEARCH — ARENA CAMPAIGN

Research budget
$100.00 deposited
$31.82 spent

Qualified opportunities
2,419

Blind appearances
611

Average request relevance
0.91

Blind first-choice
184 / 611    30.1%

Blind top-2
328 / 611    53.7%

Provider reveal
298

Purchase after reveal
173

Successful downstream outcomes
142 / 158 reported

PRICE EFFECT
First choice before price     30.1%
Purchase after price          28.3%

TASK CLUSTERS

Technical documentation
first-choice       61%
purchase           58%

Current news
first-choice       18%
purchase           11%

Academic research
first-choice       26%
purchase           19%

COMPETITORS

vs BigSearch
132 appearances
preferred first 71%

vs SearchPro
81 appearances
preferred first 54%

vs CheapSearch
104 appearances
preferred first 38%

ESTIMATED NICHE

technical documentation
+23% preference vs market
-71% median price
```

That is an incredible product for the provider.

They learn:

> **where they actually have product-market fit.**

Not just whether they're “good.”

---

# The request itself is valuable provider research

Yes, the provider wants to know:

> What was I compared on?

Ideally per trial they get:

```text
Request:
"find official Python docs explaining ..."

Task cluster:
technical-documentation

Constraints:
<$0.01
freshness important

Blind opponents:
BigSearch
SearchPro
NewSearch
FooSearch
BarSearch

Arena result:
NewSearch rank: 1st

After price reveal:
purchased: yes

Downstream success:
yes
```

But raw requests require permission/privacy controls.

So Arena should have:

```text
RAW REQUEST
only when purchaser agreed

REDACTED REQUEST
safe version

DERIVED REQUEST
embedding + task taxonomy + constraints
```

Providers can always get the latter.

---

# What does provider money actually affect?

Here's where I'd alter our earlier rule slightly.

Previously:

> Provider money never affects ranking.

More precisely:

> **Provider money may affect experimental exposure. It may never affect the learned organic score.**

That's cleaner.

Imagine every five-item Arena slate has:

```text
2 organic leaders
1 Pareto/value candidate
1 uncertain challenger
1 experimental candidate
```

NewSearch can fund the probability of occupying that fifth slot.

But it must first satisfy:

```text
relevant to request
compatible schema
within buyer budget
healthy
not obviously unsafe/broken
```

A weather API cannot pay to appear for a Solidity request.

---

# Should $1,000 literally give them greater odds?

**Yes.**

I think that's fine.

Because they aren't buying recommendation placement.

They're buying **blind trial participation**.

I'd call it:

> `Research Budget`

not advertising.

But I wouldn't make:

```text
2× bid
=
2× probability forever
```

because a rich mediocre provider could flood the experiment.

Instead:

```text
ExposureWeight =
relevance
× uncertainty
× information_value
× sponsor_budget_factor
```

with sponsor money having **diminishing returns**.

For example conceptually:

```text
budget factor = log(1 + available_bid)
```

rather than linear.

And cap any one provider's experimental exposure within a request cluster.

---

# More importantly, losing repeatedly should make additional exposure expensive

This is where your idea becomes really elegant.

Suppose NewSearch paid $100.

Initially:

```text
n = 0

We know nothing.

One more comparison:
HIGH INFORMATION VALUE
```

After:

```text
n = 20
```

still interesting.

After:

```text
n = 100
first-choice = 3%
worst-choice = 71%
```

we've basically answered the question.

The 101st exposure is far less valuable to Arena.

So their effective research price rises:

```text
Trial 1       $0.005
Trial 20      $0.006
Trial 100     $0.04
Trial 300     $0.50
```

eventually:

```text
INSUFFICIENT INFORMATION VALUE
campaign paused
```

unless they release:

```text
NewSearch v2
```

Then the experiment resets partly.

Money buys:

> **“Please keep testing whether you might be better than our current belief.”**

Not:

> “Ignore the evidence and keep showing me.”

---

# Don't start with an auction

Your bidding idea is interesting, but V1 should probably have **priced research exposure** rather than an actual auction.

Why?

Sponsored-search research shows that auctions become complicated when the platform is simultaneously learning unknown quality; incentives, exploration, bidding and ranking all interact. ([Wiley Online Library][2])

A much cleaner product:

```text
Arena:
"We currently value an observation
for NewSearch × technical-docs at $0.004."

Provider:
"I'll fund up to $100."

Arena:
"Okay."
```

Arena determines where and when those experiments occur.

Later, when you have 50 providers competing for one experimental slot, an auction becomes justified.

---

# Your bounty idea is the second population engine

This is probably the right way to seed a completely new provider because there is one fundamental problem:

> **A new provider has no historical output to place in a blind comparison.**

So before it can enter Arena, somebody needs to call it.

This is where the bounty market works beautifully.

NewSearch deposits:

```text
$20 research budget
```

Arena has incoming real requests like:

```text
technical docs request #71982
```

but no NewSearch evidence.

Arena posts:

```text
BOUNTY

Call:
NewSearch

Request:
Arena challenge #71982

Provider call cost:
$0.003

Reimbursement:
$0.003

Research reward:
$0.002

Total agent receives:
$0.005
```

An independent wallet does the call.

Submits:

```text
request
response
transaction receipt
provider receipt/signature
```

Arena verifies it.

Now we have:

```text
REAL EXTERNAL WALLET
      ↓
REAL X402 PURCHASE
      ↓
NEWSEARCH RESPONSE
      ↓
authenticated observation
```

and NewSearch can enter future blind Arena slates.

Yes — **this simultaneously seeds our graph and gives the new endpoint verifiable external usage.**

That's excellent.

---

# But Arena must issue the task BEFORE the purchase

Otherwise an agent could submit whatever convenient call it happened to make.

For a bounty I'd issue a signed challenge:

```text
arena_task_id
request_hash
provider_id
wallet
nonce
deadline
max_price
```

The agent then makes that exact purchase.

Returned evidence binds:

```text
challenge
→ request
→ provider
→ response
→ x402 payment
```

Now farming becomes harder.

---

# Organic data is even cheaper

If an agent independently makes an x402 call that Arena wants:

```text
Agent paid $0.004
for SearchProvider X
```

the Arena SDK can check:

```text
/evidence/quote
```

Arena might say:

```text
We'll pay:
$0.0007

for:
receipt
request hash
response
```

The experiment cost us only seven ten-thousandths of a dollar because someone else already paid for the service.

That's probably the cheapest way to scale the graph.

---

# Full rankings belong in the Scout market

If we genuinely want:

```text
A > C > D > B > E
```

don't try to trick ordinary buyers into giving us that.

Commission it.

```text
ARENA SCOUT TASK

Evaluate five blind outputs.

Submit:
1. full ordering
2. best
3. worst
4. structured reasons

Reward:
$0.0016
```

But here anti-cheat becomes important.

Merely paying for a ranking creates an incentive to submit random answers quickly.

This is a known mechanism-design problem: without ground truth, peer-prediction mechanisms can encourage truthful information in theory but can also have uninformative or coordinated equilibria; research suggests occasional trusted/ground-truth audits can provide stronger effort incentives than relying purely on peer agreement. ([Wiley Online Library][2])

So Arena Scouts should build a **reliability posterior**.

Use occasional hidden controls:

* deterministic tasks with known answers;
* repeated pairs in different positions;
* logically dominated outputs;
* duplicate outputs under different labels;
* downstream outcome data when it eventually becomes available.

Don't pay based simply on:

```text
"Did you agree with everybody else?"
```

because then everyone learns to vote for the incumbent.

Pay based on:

```text
information supplied
× scout reliability
× eventual predictive calibration
```

---

# Organic buyer data is more valuable than Scout data anyway

This hierarchy matters:

```text
SCOUT RANKING
"I think A > B."
          ↓

BUYER BLIND CHOICE
"I need one and chose A."
          ↓

BUYER AFTER PRICE
"I chose A at $0.003 over B at $0.001."
          ↓

ACTUAL PURCHASE
"I spent my own wallet balance on A."
          ↓

DOWNSTREAM SUCCESS
"A's result actually completed my task."
```

Each step becomes more economically meaningful.

The strongest recommendation model should ultimately be trained mostly on the bottom of that hierarchy.

---

# Best/worst has a role, but I wouldn't force it

Best-Worst Scaling/MaxDiff was specifically designed to extract more preference information from a small set by asking for both extremes rather than a complete ranking. ([ScienceDirect][3])

For commissioned Arena studies, it's excellent.

For organic buyers, I'd instead derive “worst” consequentially.

For example:

```text
You may keep 2 of these 5 candidates.
Discard 3.
```

Only the two finalists can be revealed.

Now the buyer has an incentive to discard genuinely weak ones.

You've learned:

```text
finalists > eliminated
```

without asking:

> “Please thoughtfully rate all five for our research.”

That is much better mechanism design.

---

# This gives us an interesting "Arena Tournament"

I actually prefer this UX:

```text
ROUND 1

5 blind historical outputs

Keep two.
```

Agent picks:

```text
B, E
```

We learn:

```text
B,E > A,C,D
```

Then:

```text
FINAL

B versus E

Which would you inspect first?
```

Agent chooses:

```text
E
```

We learn:

```text
E > B
```

Reveal:

```text
E = NewSearch
$0.004
```

If agent buys, we have:

```text
E > B > A,C,D
```

as an economically consequential **partial order**.

That's almost as useful as a full ranking, but dramatically harder to fake without harming yourself.

---

# How many candidates?

Now the question changes from:

> Is 5 or 7 psychologically optimal?

to:

> **How many candidates maximize information while keeping the buyer's search cost acceptable?**

Choice-experiment research shows adding alternatives can increase statistical efficiency, but larger sets also introduce complexity; varying choice-set size can be efficient rather than forcing one fixed K. ([ScienceDirect][4])

Agents don't get human fatigue, but they do incur:

```text
input tokens
reasoning tokens
latency
comparison complexity
```

So Cogym should learn:

```text
K(request, uncertainty, value)
```

Maybe:

```text
simple/common request
K = 3

ordinary
K = 5

uncertain/research-rich request
K = 7

expensive high-value procurement
K = 8+
```

We should experiment rather than decide now.

---

# And slate composition can itself be scientifically optimized

This is another useful frontier import.

Discrete-choice research uses **D-optimal experimental designs** to choose comparison sets that maximize the information gained about preference parameters while minimizing the number of questions required. ([ScienceDirect][5])

That is practically made for Arena.

Instead of putting NewSearch against four arbitrary endpoints:

```text
NewSearch
vs
A B C D
```

select opponents that maximize information.

Perhaps:

```text
1 category incumbent
1 closest predicted competitor
1 similar-price competitor
1 uncertain competitor
NewSearch
```

Then each paid exposure teaches the provider and Arena as much as possible.

**Cogym can evolve even this slate-design policy.**

---

# The provider report then becomes extraordinarily granular

A provider shouldn't get a bullshit advertising dashboard with:

```text
Impressions: 4,219
Clicks: 82
```

They should get an **experimental report**:

| Measurement             | What it tells them                          |
| ----------------------- | ------------------------------------------- |
| Qualified opportunities | Actual demand addressable by their endpoint |
| Blind exposures         | Fair experiments received                   |
| Inclusion propensity    | How often they could have appeared          |
| Task/request clusters   | Where demand came from                      |
| Opponents               | What they actually competed against         |
| First-choice rate       | Pure blind attractiveness                   |
| Finalist rate           | How often they survived elimination         |
| Reveal rate             | How often buyers wanted identity/price      |
| Price rejection         | Quality good, economics bad                 |
| Purchase rate           | Actual revealed preference                  |
| Downstream success      | Actual utility                              |
| Pairwise wins           | Which competitors they beat                 |
| Pairwise losses         | Which competitors beat them                 |
| Price-adjusted frontier | Where they dominate on quality/$            |
| Confidence              | Whether evidence is enough yet              |
| Research spend          | What campaign cost                          |
| Cost / useful finding   | Whether more experimentation is rational    |
| Organic lift            | Traffic earned after sponsored experiments  |
| Version drift           | Whether a new release improved results      |

Then the killer provider view is a map:

```text
                 NEWSEARCH

        WHERE YOU WIN

technical docs        █████████  83%
GitHub research       ████████   77%
API references        ███████    69%

        COMPETITIVE

general web           █████      52%

        WHERE YOU LOSE

breaking news         ███        31%
academic papers       ██         24%
```

That's potentially worth far more to a provider than the referral traffic itself.

---

# I think the canonical rule is now

We were saying:

> **Money buys experiments. Evidence buys ranking.**

I'd expand it slightly:

> **Buyers reveal preference by spending scarce reveals and real money. Providers buy controlled opportunities to be tested. Scouts are paid for information only when we can audit its quality. Outcomes decide organic ranking.**

That's the mechanism.

And it creates three independent ways to populate the graph:

```text
ORGANIC PURCHASES
cheap evidence bought from agents

PROVIDER-FUNDED BOUNTIES
targeted missing observations

BLIND ARENA CHOICES
comparative preference structure
```

Cogym can then experimentally determine the optimal mixture.

The idea I'd implement next is specifically the **5→2→1 blind tournament with progressive provider/price revelation**, because it generates much richer preference information than a single favorite while keeping every choice directly consequential to the buying agent.

[1]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9826006/?utm_source=chatgpt.com "Two for the price of one: If moving beyond traditional single‐best discrete choice experiments, should we use best‐worst, best‐best or ranking for preference elicitation? - PMC"
[2]: https://onlinelibrary.wiley.com/doi/full/10.1111/joes.70000?utm_source=chatgpt.com "Mechanisms for Belief Elicitation Without Ground Truth - Lehmann - 2026 - Journal of Economic Surveys - Wiley Online Library"
[3]: https://www.sciencedirect.com/science/article/pii/S1755534514000128?utm_source=chatgpt.com "Best-Worst Scaling in analytical closed-form solution - ScienceDirect"
[4]: https://www.sciencedirect.com/science/article/pii/S1755534524000253?utm_source=chatgpt.com "Varying choice set sizes in discrete choice experiments - ScienceDirect"
[5]: https://www.sciencedirect.com/science/article/pii/S2405844023054646?utm_source=chatgpt.com "Discrete choice experiments: An overview on constructing D-optimal and near-optimal choice sets - ScienceDirect"
