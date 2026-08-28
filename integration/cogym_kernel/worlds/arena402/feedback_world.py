from __future__ import annotations
from dataclasses import dataclass
from cogym_kernel.kernel.contracts import ActionResult,ActionSpec,Metric,MetricVector,WorldSpec
from cogym_kernel.worlds.registry import register

@dataclass(frozen=True)
class State:
    seed:int
    chosen:str|None=None
    result:object|None=None

@register("arena402.feedback_lab","Consequential reveal vs commissioned ranking feedback mechanisms")
def create_feedback_world(**kwargs):return ArenaFeedbackWorld(k=int(kwargs.get("k",5)))

class ArenaFeedbackWorld:
    def __init__(self,k:int=5):self.k=k;self._spec=None
    @property
    def world_spec(self):
        if self._spec is None:
            self._spec=WorldSpec(world_kind="arena402.feedback_lab",version="1",instance_set_hash=f"feedback-k{self.k}-v1",environment_hash="arena-feedback-sim-v1",oracle_hash="latent-utility-order",metadata={"k":self.k})
        return self._spec
    @property
    def worldpack_id(self):
        from cogym_kernel.kernel.ids import content_id
        return content_id("wp",{"kind":"arena402.feedback_lab","v":1,"k":self.k})
    def reset(self,*,instance_id:str,seed:int):return State(seed)
    def observe(self,state):return {"k":self.k,"goal":"maximize truthful preference information per comparison cost"}
    def actions(self,state):
        if state.chosen:return ()
        return tuple(ActionSpec(kind="SELECT_FEEDBACK",payload={"mechanism":m},executor_kind="deterministic") for m in ("favorite_reveal","tournament_5_2_1","best_worst_scout","full_rank_scout"))
    def apply(self,state,action,result):
        from arena402.feedback_simulation import FeedbackConfig,run_feedback_episode
        m=action.payload["mechanism"];r=run_feedback_episode(seed=state.seed,mechanism=m,cfg=FeedbackConfig(k=self.k))
        return State(state.seed,m,r)
    def terminal(self,state):return state.chosen is not None
    def score(self,state):
        r=state.result
        return MetricVector(metrics=(Metric("pairwise_precision",float(r.pairwise_precision),"max"),Metric("information_per_cost",float(r.information_per_cost),"max"),Metric("comparison_cost",float(r.comparison_cost),"min"),Metric("low_effort",1.0 if r.low_effort else 0.0,"min")))
