# 402Arena — Best Mechanisms and Why They Work

**Date:** 2026-08-28

---

## 1. D-Optimal Slate Selection

**File:** `arena402/retrieval.py:53-76`, `arena402/slate.py:45-78`

**What it does:** Selects candidates for the blind tournament to maximize information gain.

**How it works:**
- **Incumbent**: highest-scoring provider (exploitation)
- **Closest**: second-highest (competition)
- **Cheapest**: lowest price (price sensitivity test)
- **Uncertain**: fewest observations (exploration)
- **Challenger**: lowest-ranked (new entrant opportunity)

Then deduplicates while preserving diversity. Fills remaining slots from ranked list.

**Why it works:** Each slot serves a different experimental purpose. You're not just picking the best — you're designing an experiment. The D-optimal proxy (determinant of feature Gram matrix) ensures maximum information per observation.

**Evidence:** K=4 with D-optimal slots achieves net utility 0.832, higher than random (0.81) or incumbent-only (0.79).

---

## 2. Scarce 5→2→1 Tournament

**File:** `arena402/choice.py:22-53`, `arena402/arena40254-scarcity-mechanic-verbatim.md`

**What it does:** Forces consequential choice by limiting reveal credits.

**How it works:**
1. Show 5 blind candidates
2. Buyer picks 2 finalists
3. Reveal first finalist (provider + price)
4. Buy? YES → done. NO → reveal second finalist
5. Buy? YES → done. Skip → record elimination

**Why it works:**
- Buyer can't see all 5 (wastes reveal on garbage → hurts self)
- Each reveal produces a partial ordering point: C > A > remaining
- Buyer MUST actually read the outputs (can't cheat)
- Full reveal gives 100% best==purchase (no economic signal). Scarce gives 79.6% (20.4% switch)

**Evidence:** H2 CONFIRMED. 79.6% vs 100%. Greedy archetype: +26pp switch (most price-sensitive).

---

## 3. SeparatedSlatePolicy

**File:** `arena402/slate.py:81-230`

**What it does:** Keeps organic ranking and sponsored research exposure completely separate.

**How it works:**
- Organic slots scored by: 0.62 × quality × freshness + 0.23 × demand × uncertainty + 0.10 × novelty + 0.05 × sponsor_exposure
- Research slots scored by: sponsor budget, separate allocation
- Sponsor balance is NEVER read for organic scoring

**Why it works:** Providers can buy measurement opportunities (more data points about their quality) but never buy ranking position. This is the critical invariant that makes Arena trustworthy.

**Evidence:** H1 CONFIRMED. `separated_ids` achieves quality 0.901 (same as `paid_rank_bad`) but with honest exposure. `organic_only` never discovers new providers (0 appearances).

---

## 4. DiscountedContextualBeta

**File:** `arena402/bandits.py`

**What it does:** Tracks provider quality beliefs with time decay.

**How it works:**
- Beta distribution per (task, provider) pair
- 700-step half-life: recent evidence matters more
- Uncertainty = sqrt(variance + 1/(n+1))
- Higher uncertainty → larger slate (adaptive K)

**Why it works:** New providers start with high uncertainty (gets them sampled). Old providers with stable quality converge (stops wasting budget). Time decay handles provider quality changes.

---

## 5. VOI-Based Exploration Budget

**File:** `arena402/exploration.py:12-95`

**What it does:** Decides which providers deserve subsidized inspection.

**How it works:**
```
voi = 0.30 × novelty      (1 / sqrt(1 + provider_evidence_mass))
    + 0.25 × uncertainty   (sqrt(variance + 1/(n+1)))
    + 0.20 × demand        (log(1 + total_mass) / log(25))
    + 0.15 × staleness     (1 - 0.5^(age / half_life))
    + 0.10 × coverage_gap  (1 / sqrt(1 + provider_evidence_count))
```

Subsidy = min(max_subsidy, normal_price × voi, balance)

**Why it works:** Providers with high novelty (new) + high uncertainty (unknown quality) + high demand (frequently requested) + stale evidence (needs refresh) + coverage gaps (under-represented) get the most exploration budget. This is optimal for discovering hidden winners.

---

## 6. Evidence Market Bid Curve

**File:** `arena402/evidence_market.py:43-140`

**What it does:** Prices evidence based on expected value of information.

**How it works:**
```
value_score = evidence_strength × future_transfer × (
    0.38 × uncertainty +
    0.27 × saturation +
    0.22 × demand +
    0.13 × freshness
)
```

Bids saturate as evidence mass accumulates. Organic evidence cheaper than commissioned.

**Why it works:** Evidence is worth more when:
- Routing uncertainty is high (we don't know which provider is best)
- Coverage is low (we haven't seen this provider-task pair much)
- Demand is high (many agents will use this routing decision)
- Evidence is stale (quality may have changed)

**Evidence:** H8 CONFIRMED. Bids drop from $0.008 to $0.002 as mass >200.

---

## 7. Wash Detection (6 Checks)

**File:** `arena402/anti_cheat.py:19-57`

**What it does:** Detects gaming via multiple signals.

**Checks:**
1. Self-dealing (buyer == provider): risk +0.95
2. Repeated wallet pair (≥10 transactions): risk +0.05×log
3. Request reuse (≥5 same hash): risk +0.25
4. Response reuse (≥5 same hash): risk +0.25
5. Transaction replay (duplicate tx_hash): risk = 1.0
6. Heavy buyer activity: tracked for anomaly detection

**Why it works:** No single check catches everything. Combined, they create a robust first-line defense. Threshold 0.5 cleanly separates self-dealing (1.0) from clean behavior (0.0).

**Evidence:** H5 CONFIRMED. Clean live wash=0.0 vs self-deal wash=1.0.

---

## 8. BWS (Best-Worst Scaling) Anti-Cheat

**File:** `arena402/anti_cheat.py`, experiment logs

**What it does:** Makes random cheating unprofitable.

**How it works:** Under full ranking, a random guesser gains $0.001. Under BWS scarce reveals, a random guesser loses $0.0007. The scarcity makes information have value, so wasting it on random choices hurts.

**Why it works:** If you can't see all candidates, picking randomly is worse than picking strategically. BWS extracts maximum information from minimum reveals.

**Evidence:** H4 CONFIRMED. Delta = 0.0017.

---

## 9. Progressive Paid Reveal (Moltwork)

**File:** `/root/repute/src/commitment.py`, `/root/repute/src/reveal.py`

**What it does:** Merkle-commit content, reveal chunks proportional to payment.

**How it works:**
- Text chunked into coherent units (200-400 tokens)
- Each chunk salted + SHA-256 hashed → Merkle tree
- Content XOR-encrypted (placeholder for AES-GCM)
- Buyer pays per chunk; deterministic random reveal order (HMAC-SHA256 Fisher-Yates)
- Invariant: `money_paid / list_price == content_revealed / total_units`

**Why it works:** Sellers can't concentrate quality in previews. Buyers can't strategically request the conclusion. Every cent spent reveals proportional content.

---

## 10. Provider Lifecycle

**File:** `arena402/mechanism.py:20-27`

**What it does:** Tracks provider maturity through states.

**States:**
```
UNSEEN → SEEDED → CHALLENGER → ORGANIC
                    ↓
              ELIMINATED
                    ↓
                PAUSED
```

**Why it works:** New providers get exploration budget (SEEDED). If they perform well, they become CHALLENGERs competing with incumbents. If they prove themselves, they become ORGANIC. If they fail, they're ELIMINATED. This prevents both stagnation (incumbents never lose) and waste (bad providers never get cut).
