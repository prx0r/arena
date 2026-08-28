# Report 4 — Hermes -z Batch + Evolve

**Logs:** `hermes_z_batch.jsonl:3` `29.1s avg` + `evolve_proposals.jsonl:5`.

**Hypothesis:** `ox-alpha-free` primary with `mimo-v2.5` fallback is viable; evolve `k/thr/VoI` via `Cogym recipes` on live `20%` switch.

**Results:**
- `hermes_z_batch models {'mimo-v2.5 (fallback)': 1, 'ox-alpha-free': 2} dur avg 29.1s` — ox-alpha 25-35s (often empty `No reply`) then mimo succeeds.
- Evolve candidates from `live 9 scarce 250`: `k 3 wash 0.4 sim 0.15` etc `evolve_proposals 5` `k 3-4` proposed.

**Proves:** Fallback chain works but ox-alpha flaky (empty) — need robust JSON prompt. Evolve loop ready (logs→Hydra→propose). **H3 PROVISIONAL** (`k=4 0.833` synthetic but live fixed 5).

**Drives:** Switch daemon to `k∈{3,4,5,6}` adaptive per `uncertainty` (`exploration.py:97`), log `k` in receipt, next `mechanism_sweep --rounds 1200` will confirm.
