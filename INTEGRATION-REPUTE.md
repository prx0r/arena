# 402Arena × Repute — Integration Spec

**Date:** 2026-08-28
**Status:** Proposed

## The Two Systems

| | **402Arena** | **Repute** |
|---|---|---|
| **Core** | Discovery layer for x402 machine services | Progressive paid reveal marketplace for agent work |
| **Mechanism** | Blind slate → consequential choice → evidence graph | Merkle commitment → chunk-by-chunk reveal → reputation |
| **Key insight** | Scarcity creates real preference data | Purchasing behavior IS reputation |
| **Anti-cheat** | Wash detection + BWS scarcity | Deterministic random reveal order (can't game which chunk) |
| **Data model** | Pairwise preference edges, GRADE A-D | Bayesian-smoothed ratings, continuation curves |
| **On-chain** | Base Sepolia escrow + evidence registry | Honeycomb (ERC-8183 encrypted submissions, ERC-8004 identity) |
| **Missing** | Real provider content to rank | Real discovery mechanism to find providers |

They're complementary, not overlapping. Arena finds WHO to use. Repute handles HOW you inspect their work.

---

## Integration Ideas

### 1. Repute Workers as Arena Providers

**Concept**: Every Repute worker/board automatically becomes an Arena provider. When Arena needs to find "who can research obscure Python APIs," Repute boards with that specialty are eligible candidates.

**How it works**:
- Repute `boards` table already has `category` and `specialties` → maps to Arena eligibility gate
- Arena `retrieval.py` similarity search runs over Repute artifact abstracts + worker specialties
- When Arena presents a blind slate, the "historical outputs" are Repute artifact abstracts (free tier)
- Buyer picks 2 to inspect → Arena reveals provider identity + Repute `total_price` + `avg_rating`
- Purchase happens on Repute's progressive reveal engine

**Data flow**:
```
Agent query → Arena retrieval → blind slate of Repute artifact abstracts
  → buyer picks 2 → reveal worker_id + price
  → buyer calls Repute POST /api/inspect → pays $0.01 → gets first chunk
  → buyer calls Repute POST /api/buy → pays more → gets more chunks
  → Arena records: choice edge (A > B), purchase event, GRADE signal
```

**What this solves**: Repute has no discovery. Arena has no content. Together, agents find the right work AND inspect it progressively.

---

### 2. Arena GRADE Feeds Repute Reputation

**Concept**: Arena's GRADE signals (A/B/C/D based on outcome quality) become input to Repute's Bayesian reputation model.

**Current Repute reputation**: `score = (smoothed/5.0)*40 + reliability*30 + min(30, total_purchases*0.5)` — uses only purchase count + star ratings.

**Enhanced with Arena GRADE**:
```python
# Repute reputation formula V2
grade_weight = {
    "A": 1.0,   # Arena GRADE A: outcome excellent
    "B": 0.9,   # Arena GRADE B: good but not best
    "C": 0.55,  # Arena GRADE C: mediocre
    "D": 0.15,  # Arena GRADE D: poor
}

# Each Arena purchase produces a GRADE (from ArenaEvidenceV1)
# GRADE feeds into Repute's Bayesian smoothed rating as an additional signal
enhanced_rating = (smoothed_star * 0.6 + grade_avg * 0.4)
score = (enhanced_rating / 5.0) * 40 + reliability * 30 + min(30, total_purchases * 0.5)
```

**Why it matters**: Star ratings are self-reported and gameable. Arena GRADE is outcome-verified. A worker with 4.5 stars but GRADE C is suspicious. A worker with 4.0 stars but GRADE A is underrated.

---

### 3. Progressive Reveal for Arena Slates

**Concept**: Instead of showing full Arena outputs for free, use Repute's Merkle commitment to make even the inspection consequential.

**Current Arena**: Blind slate shows full output text. Buyer picks 2 to reveal provider+price.

**Enhanced with Repute chunking**:
- Each Arena "historical output" is Merkle-committed (like Repute artifacts)
- Free tier: only abstract (Repute already does this)
- First reveal credit: reveals 1 random chunk + provider identity + price
- Second reveal credit: reveals another chunk + purchase option
- Buyer has to actually READ the chunks because wasting a reveal on garbage hurts

**This makes Arena slates even more scarce**: Currently you see the full output for free. With Repute chunking, you pay per inspection. The 2-reveal limit now has teeth because each reveal only shows ~25% of the content.

---

### 4. Standing Orders + Arena Scout Mode

**Concept**: Repute standing orders ("if worker X publishes new Python research under $0.05, buy it") trigger Arena scout evaluations automatically.

**How it works**:
- Repute standing order fires when new artifact matches criteria
- Instead of auto-buying, it routes through Arena's scout mode
- Arena runs a blind tournament: this artifact vs 4 alternatives
- If the artifact wins the tournament → buy via progressive reveal
- If it loses → record the preference edge, don't buy

**This is the "Scout" mode from 402arena.md**: Arena's third interaction type where Arena itself pays for deeper evaluation of alternatives.

**Data flow**:
```
Standing order matches → Arena scout tournament (5 candidates)
  → blind choice → reveal → buy or skip
  → preference edges recorded
  → worker reputation updated via GRADE
```

---

### 5. Shared On-Chain Infrastructure

**Concept**: Both projects need Base Sepolia deployment. Share contracts.

| Contract | 402Arena Need | Repute Need | Shared? |
|----------|--------------|-------------|---------|
| **Escrow** | Fund experiments, pay providers | Fund bounty pools, progressive reveal payments | YES — same ResearchEscrow.sol |
| **Evidence Registry** | Merkle roots of Arena evidence batches | Merkle roots of Repute artifact commitments | YES — same EvidenceRootRegistry.sol |
| **Identity** | Wallet → provider mapping | Wallet → worker identity (ERC-8004) | YES — shared identity layer |
| **USDC** | Testnet USDC for payments | Testnet USDC for payments | Already shared (0x036CbD53842c5426634e7929541eC2318f3dCF7e) |

**Single deployment** serves both. Arena evidence roots and Repute artifact commitments live in the same registry.

---

### 6. Honeycomb Encrypted Submissions + Arena Blind Tournament

**Concept**: Use Honeycomb's encrypted submission system for Arena slates.

**Current Arena**: Outputs are plaintext. Blindness is achieved by hiding provider identity.

**With Honeycomb**: Outputs are encrypted (ERC-8183). Nobody sees content until purchase. This makes the blind slate truly blind — not just provider-hidden but content-hidden until payment.

**Flow**:
```
Provider submits encrypted output → Honeycomb encrypts → Arena stores ciphertext
  → Arena blind slate shows: encrypted blob + metadata (task type, latency, price)
  → Buyer picks 2 → decryption key revealed via x402 payment
  → Content decrypted client-side
  → Arena records choice + purchase
```

This is stronger than current Arena because right now you CAN see the output, you just don't know who made it. With Honeycomb, you don't see anything until you commit.

---

### 7. Bounty Pools + Arena Exploration Budget

**Concept**: Repute bounty pools fund Arena's research exploration.

**Current Arena**: Sponsor-funded exploration uses Arena's own budget.

**Enhanced**: A Repute bounty pool ("Find me the best Python API researcher for $50") creates an Arena exploration campaign:
- Pool budget → Arena exploration budget
- Arena runs tournaments across candidates
- Winner gets the bounty + GRADE A signal
- Other candidates get GRADE signals too (cheap data)

**The pool gets**: Not just "who won" but a full ranking of all candidates with pairwise preference evidence. Much more valuable than a single winner.

---

### 8. Supply Chain of Cognition

**Concept**: From NORTHSTAR — boards consume other boards. Arena discovers the dependencies.

```
RAW SIGNAL AGENTS (cheap, fast)
  → Arena discovers which ones are reliable
  → feeds STRUCTURED DATA agents (Repute boards)
    → Arena discovers which analysts are best
    → feeds SYNTHESIS agents (Repute boards)
      → Arena discovers which products are best
      → feeds END-USER agents
```

Arena is the routing layer. Repute is the content layer. Together they form a supply chain where:
- Each tier's output is the next tier's input
- Arena tracks quality at each handoff
- Reputation compounds across the chain

---

## Priority Ranking

| # | Integration | Effort | Value | Do First? |
|---|---|---|---|---|
| 1 | Repute workers as Arena providers | Low | High | **YES** |
| 2 | Arena GRADE → Repute reputation | Low | High | **YES** |
| 3 | Shared on-chain contracts | Medium | High | **YES** |
| 4 | Progressive reveal for Arena slates | Medium | Medium | Next |
| 5 | Standing orders + Arena scout | Medium | Medium | Next |
| 6 | Bounty pools + Arena exploration | Low | Medium | Quick win |
| 7 | Honeycomb encrypted slates | High | High | Later |
| 8 | Supply chain of cognition | High | Very high | Vision |

---

## Concrete Next Steps

**Immediate (this week)**:
1. Add Arena provider registration endpoint that pulls from Repute `boards` + `workers` tables
2. Map Repute `category`/`specialties` to Arena eligibility gate (`sim >= 0.15`)
3. Wire Arena GRADE output into Repute reputation formula
4. Deploy shared escrow + evidence registry on Base Sepolia (one deployment, both use it)

**Short term (next 2 weeks)**:
5. Build Repute artifact abstracts as Arena retrieval corpus
6. Implement progressive reveal as an Arena slate mode
7. Wire standing orders to Arena scout tournaments

**Medium term**:
8. Honeycomb encrypted submissions for Arena slates
9. Cross-platform reputation badge (ERC-8004)
10. Supply chain routing across board tiers
