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

There is real choice-modeling evidence for this problem: best/worst and ranking can extract more statistical information than asking only for a first choice, but the preferences inferred from deeper choices can differ from the first-choice utility, and later choices can be less consistent.

So I'd make **organic buyer feedback consequential**, while paying separately for deeper scientific evaluation.

# The buyer mechanic I'd use

Suppose the agent asks:

> Find me an x402 that can research obscure Python API documentation.

Arena finds five historical outputs relevant to that intent.

We show:

BLIND ARENA

A  [historical output]
B  [historical output]
C  [historical output]
D  [historical output]
E  [historical output]

Providers hidden.
Prices hidden.

But don't say:

> rank 1–5 and we'll show everything.

Because:

random ranking
→ all information unlocked

is a perfectly rational cheap strategy.

Instead give the agent **two reveal credits**.

> “Which two would you actually want to investigate?”

That choice matters.

If it chooses:

C
A

we reveal only:

C = NewSearch
current price: $0.003

A = BigSearch
current price: $0.019

Now we have a strong preference:

C,A > B,D,E

and some weaker ordering:

C > A

depending on whether we asked them sequentially.

The agent had to actually look at the outputs because wasting one of its two reveals on garbage hurts **it**.

That's much stronger anti-cheat than saying:

> “Please rank honestly.”

---

# Make it sequential and we get even more

I'd actually implement this:

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

Now every reveal produces another point in a **partial ranking**:

C > A > remaining alternatives

but only insofar as the buyer actually needed to keep searching.

That is exactly the kind of data we want.

An agent that immediately buys C gives us:

C was first blind choice
C survived price reveal
C was actually purchased

Very strong.

An agent that chooses C blind but rejects it after discovering $0.08, then buys A at $0.004, gives us two separate things:

QUALITY PREFERENCE
C > A

ECONOMIC PREFERENCE
A > C at observed prices

That distinction is extremely valuable.
