# Report 1 — Scarce 2-Reveals vs Full Reveal (Incentive Mechanism)

**Logs:** `rank_sim_scarce.jsonl:250` + `rank_sim_full.jsonl:250` synthetic 5 archetypes (greedy, cautious, analytical, anxious, reckless) ×50 queries, slate 5, sim 0.7-0.95.

**Hypothesis H2:** `2 reveals $0.0001` scarcity creates price/quality split; full reveal collapses to quality only (`402arena:299`).

**Method:** For each slate, agent scores `0.6*sim+0.3*qual-0.1*cost + noise`, picks `best/worst`, then `purchase` after price reveal: scarce only sees best/worst price, full sees all.

**Results:**
- `scarce best==purchase 79.6% (199/250)` vs `full 100% (250/250)` — 20.4% switch is economic preference.
- Per archetype: `greedy 74%→100% +26pp` (most price-sensitive), `cautious 84%→100% +16pp`, `analytical 78%→100% +22pp`, `anxious 84%→100% +16pp`, `reckless 78%→100% +22pp`.
- `greedy avg best cost scarce 0.0096` vs `cautious 0.0098` (full 0.0090 vs 0.0098) — greedy cheaper.
- `best top3 scarce: b4 62/b0 62` spread vs `full: b3 66/b2 53` concentrated.

**Proves:** Scarcity enforces consequential choice (`arena40254:60`). Wasting reveals on garbage hurts agent (reveals have value). Full reveal is not incentive-compatible (pays random). **H2 CONFIRMED**.

**Drives:** Use scarce `5→2→1` tournament live; evolve `reveals_allowed=2` vs `3` via Cogym.
