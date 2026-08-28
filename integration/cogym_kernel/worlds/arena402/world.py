from __future__ import annotations

from dataclasses import dataclass
from cogym_kernel.kernel.contracts import ActionResult, ActionSpec, Metric, MetricVector, WorldSpec
from cogym_kernel.worlds.registry import register


@dataclass(frozen=True)
class State:
    seed: int
    chosen: str | None = None
    result: object | None = None


@register("arena402.mechanism_lab", "x402 routing + research-market mechanism design replay")
def create_world(**kwargs):
    return ArenaMechanismWorld(rounds=int(kwargs.get("rounds", 800)))


class ArenaMechanismWorld:
    def __init__(self, rounds: int = 800):
        self.rounds = rounds
        self._spec = None

    @property
    def world_spec(self) -> WorldSpec:
        if self._spec is None:
            self._spec = WorldSpec(
                world_kind="arena402.mechanism_lab",
                version="2",
                instance_set_hash="arena402-synthetic-cold-start-v2",
                environment_hash="arena402-sim-v2",
                oracle_hash="latent-provider-utility-v2",
                metadata={"rounds": self.rounds, "policies": ["organic_only","random_explore","paid_rank_bad","separated_ids"]},
            )
        return self._spec

    @property
    def worldpack_id(self) -> str:
        from cogym_kernel.kernel.ids import content_id
        return content_id("wp", {"kind":"arena402.mechanism_lab","v":2,"rounds":self.rounds})

    def reset(self, *, instance_id: str, seed: int) -> State:
        return State(seed=seed)

    def observe(self, state: State) -> dict:
        return {
            "scenario":"new cheap niche provider enters established x402 market",
            "provider_count":12,
            "sponsor_budget_usd":50.0,
            "goal":"maximize buyer utility while discovering useful challengers cheaply",
            "rounds":self.rounds,
        }

    def actions(self, state: State) -> tuple[ActionSpec, ...]:
        if state.chosen is not None:
            return ()
        return tuple(ActionSpec(kind="SELECT_MECHANISM",payload={"policy":p},executor_kind="deterministic") for p in (
            "organic_only","random_explore","paid_rank_bad","separated_ids"
        ))

    def apply(self, state: State, action: ActionSpec, result: ActionResult) -> State:
        from arena402.simulation import ArenaSimulation
        policy = action.payload["policy"]
        sim = ArenaSimulation(seed=state.seed, policy=policy).run(self.rounds)
        return State(seed=state.seed, chosen=policy, result=sim)

    def terminal(self, state: State) -> bool:
        return state.chosen is not None

    def score(self, state: State) -> MetricVector:
        r=state.result
        if r is None:
            return MetricVector(metrics=(Metric("buyer_utility",0.0,"max"),))
        discovery = float(self.rounds + 1 if r.discovery_round is None else r.discovery_round)
        paid_rank_corruption = 1.0 if state.chosen == "paid_rank_bad" else 0.0
        return MetricVector(metrics=(
            Metric("buyer_utility",float(r.mean_buyer_utility),"max"),
            Metric("realized_quality",float(r.mean_realized_quality),"max"),
            Metric("research_spend_usd",float(r.research_spend_usd),"min"),
            Metric("discovery_round",discovery,"min"),
            Metric("new_provider_purchases",float(r.newseed_purchases),"max"),
            Metric("paid_rank_corruption",paid_rank_corruption,"min"),
        ))

# Register companion feedback world when Cogym imports this package world module.
from . import feedback_world as _feedback_world  # noqa: E402,F401
