# API Budgets — rate limits as first-class harness config

Worlds that call external APIs must declare their limits. The harness counts
every call, respects `rpm`/`rpd`, and warns before a round would take too long.

## Declare limits

**1. Install the API's docs** — copy the rate-limit page to `docs/apis/<api>.md`
(e.g. `docs/apis/tavily.md` — paste the "Rate Limits: 60 req/min" table). This
is the source of truth for `rpm`/`rpd` and is reviewed like code.

**2. Fill `manifest.json:api_limits`** — generated with an example:

```json
"api_limits": {
  "tavily": {"rpm": 60, "rpd": 1000},
  "openai": {"rpm": 3500}
}
```

Remove `example_tavily` once you add real entries. No `api_limits` → harness
assumes no external calls (deterministic world).

## How it works

```python
from cogym_kernel.ratelimit import ApiBudget, RateLimitedExecutor

budget = ApiBudget(rpm=60, rpd=1000)  # from manifest
executor = RateLimitedExecutor(TavilyExecutor(...), budget)

# Before a campaign: estimate and warn
planned = n_episodes * calls_per_episode
if msg := budget.check(planned):
    print(msg)
    # "WARNING: this round will take ≥12.3min at 60 rpm (740 calls) — amend strategy or is that ok?"

# During execution: every execute() auto-counts and sleeps to respect rpm
```

Counts live in `MetricVector` as `api_calls:{api}` so recipes evolve toward
API-efficient harnesses and Hydra stores per-run usage for later queries.

## Autonomous loop integration

The orchestrator calls `budget.check(planned)` before `run_suite_parallel`.
If it returns a warning, the harness logs it to the receipt and (in autonomous
mode) asks to amend strategy. `BLOCKED` (would exceed `rpd`) aborts the round.

Wiring is one line: wrap the executor, declare limits, done. No world code
changes.
