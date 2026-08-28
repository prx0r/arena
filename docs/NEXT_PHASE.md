# Next Phase — Autonomous 402Arena Evolution

**Based on 541 receipts analysed: scarce creates 20% price-switch vs full 0%, wash clean 0.0 vs 1.0 self-deal, hermes -z ox-alpha → mimo fallback working (29s avg).**

## 1. Hidden controls for Scout reliability (arena40254:751)
- **Deterministic tasks:** add 10% of slates where answer is known (e.g., "2+2=4" with 4 variants, only one correct). Scout must pick correct.
- **Repeated pairs:** same A vs B in different positions/shuffled; reliability = consistency
- **Dominated outputs:** one output logically strictly worse (empty, truncated); picking it = fail
- **Implementation:** `arena402/anticheat.py:22` `scout_reliability()` Beta posterior `(success+2)/(total+4)` already; add `store HiddenControl` table, tag `provider_id=control`, exclude from ranking, only for calibration.

## 2. D-optimal opponent selection (arena40254:975)
- Current MMR `retrieval.py:59` is provider-diversity only.
- **Next:** `1 incumbent +1 closest competitor +1 price competitor +1 uncertain + NewSearch` per `402arena:497` ResearchValue. Compute `information_gain` per candidate as `uncertainty * novelty` from `exploration.py:31` `score()`, then greedy maximize determinant of Fisher info (approx by picking max `info` not just diversity).
- Evolve weights `αβγδ` in `S*` via Cogym.

## 3. Privacy tiers RAW/REDACTED/DERIVED (arena40254:369)
- **RAW:** only when buyer opts in (`store.observations.public_example` already)
- **REDACTED:** safe version (strip PII via regex, keep task)
- **DERIVED:** embedding + task taxonomy + constraints (always allowed) for provider report.
- Add to `report.py:5` `privacy_tier` field.

## 4. Full 22-row dashboard (arena40254:1001)
- Current `report.py` 6 fields → expand to 22: qualified_opportunities, blind_exposures, inclusion_propensity, task_clusters, opponents, first_choice_rate, finalist_rate, reveal_rate, price_rejection, purchase_rate, downstream_success, pairwise_wins/losses, price_adjusted_frontier, confidence, research_spend, cost_per_finding, organic_lift, version_drift, etc.
- Include niche map `technical docs 83%` style.

## 5. Adaptive K evolution (402arena:362)
- Live `k=5` fixed `live_arena_hermes_oxalpha.jsonl`. Next: `adaptive_k(uncertainty)` `3 if <0.25 else 4/5/6` (`exploration.py:97`) with `is_arena_trial` → `6` when uncertainty>0.6. Log `k` in receipt, Hydra `REL_RAN_ON` will show `k=3` utility vs `k=6` info tradeoff. Cogym `propose_children` will discover optimum.

## 6. Autonomous live loop (hermes kanban + Hydra)
- **Loop:** `hermes kanban list --json | claim <id> → EvidenceRetriever.search(mode=arena, k=adaptive) → hermes -z ox-alpha (fallback mimo) → record_best_worst/tournament → wash_score → log JSONL → complete kanban → Hydra batch `ensure_node` + `REL_RAN_ON` → receipts canonical`
- **Rate:** respect `manifest.json:api_limits` `AGENTS.md:11` (`--max-runtime` per kanban task)
- **Idempotency:** `job_id` + `run_id=blake3` handles `HERMES.md:33` double-claim race.

## 7. Chain (minimal)
- Stay `base-sepolia-sim` until 100 receipts, then EAS `arena-evidence-v1` batch `≤64` `SPEC.md:47` on Base Sepolia `alch_GX8...` `0x2bc7a51` — ~$1 per 1000 attestations.

**Run now:** `scripts/hermes_live_loop.py` continuous, `logs/live_hermes_z.jsonl` → `cogym evolve` on `wash_score <0.5` + `best==purchase` rate.
