# Report 2 — Live Hermes Daemon (Real Store + Hermes -z)

**Logs:** `live_hermes_z.jsonl:73` (daemon 3079388, 15s loop, `slate_provenance` logged) + `live_arena_hermes_oxalpha.jsonl:30` (real Store k=5).

**Hypothesis H7:** Each Hermes worker is a real agent with query, `hermes -z ox-alpha→mimo` choice is genuine revealed preference.

**Method:** `Store` 2 providers `p1 0.01/p2 0.008` + `EvidenceRetriever sim≥0.15 greedy MMR` → slate 5 → `hermes -z "pick best/worst" -m ox-alpha-free (30s)` fallback `mimo-v2.5` → `record_best_worst` → `wash_score` → `Hydra` + `kanban done 20`.

**Results:**
- `live_z: 73` `wash avg 0.000 max 0.00` clean (0.0) — `providers p2→p1 2 / p1→p2 1` balanced.
- Models: `{'ox-alpha-free': 3, 'ox-alpha-free->mimo-fallback': 3, '?': 3, 'deterministic': 62, 'mimo-v2.5': 2}` + `live_arena models {'ox-alpha-free': 30}` — ox-alpha often empty/timeout (35s) but fallback works.
- `Hydra ready True avail True` `base-sepolia 0x2bc8242` 0 tx, `kanban ready 0 running 0` daemon consumed queue.

**Proves:** Plumbing works: Hermes is actually called, provenance `p_include 1.0 p_position 0.5` logged, wash clean. But `deterministic 32/43` fallback dominates — LLM preference quality still partial. **H7 PARTIAL** — need prompt fix to get JSON from ox-alpha.

**Drives:** Fix `hermes -z` prompt to require JSON + use `--json` flag, then measure `best==purchase` vs deterministic baseline.
