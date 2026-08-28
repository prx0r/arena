from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
import math
import random
from collections import defaultdict

from .bandits import DiscountedContextualBeta
from .choice import validate_tournament
from .evidence_market import CoverageBook, EvidenceMarket
from .mechanism import CampaignState, EvidenceGrade, MechanismConfig, ProviderArm, ProviderCampaign, RequestContext
from .slate import DemandModel, SeparatedSlatePolicy
from .sponsor import CampaignBook


TASKS = ("coding", "research", "extraction", "fresh-search")


@dataclass(frozen=True)
class LatentProvider:
    provider_id: str
    price_usd: float
    qualities: dict[str, float]
    latency_ms: float
    failure_rate: float = 0.0
    sponsor_budget_usd: float = 0.0
    version: str = "1"


DEFAULT_MARKET = (
    LatentProvider("incumbent", 0.0100, {"coding":0.84,"research":0.86,"extraction":0.81,"fresh-search":0.91}, 900),
    LatentProvider("mid",       0.0030, {"coding":0.79,"research":0.78,"extraction":0.83,"fresh-search":0.77}, 650),
    LatentProvider("cheap",     0.0007, {"coding":0.66,"research":0.63,"extraction":0.72,"fresh-search":0.65}, 420),
    LatentProvider("flaky",     0.0020, {"coding":0.82,"research":0.80,"extraction":0.80,"fresh-search":0.79}, 500, 0.25),
    LatentProvider("extractor", 0.0022, {"coding":0.55,"research":0.60,"extraction":0.94,"fresh-search":0.50}, 700),
    LatentProvider("fast",      0.0018, {"coding":0.74,"research":0.69,"extraction":0.76,"fresh-search":0.82}, 210),
    LatentProvider("academic",  0.0060, {"coding":0.68,"research":0.92,"extraction":0.70,"fresh-search":0.73}, 1200),
    LatentProvider("news",      0.0040, {"coding":0.61,"research":0.72,"extraction":0.67,"fresh-search":0.95}, 450),
    LatentProvider("structured",0.0032, {"coding":0.76,"research":0.74,"extraction":0.90,"fresh-search":0.68}, 730),
    LatentProvider("general",   0.0025, {"coding":0.77,"research":0.76,"extraction":0.78,"fresh-search":0.76}, 610),
    LatentProvider("budget",    0.0004, {"coding":0.58,"research":0.57,"extraction":0.63,"fresh-search":0.61}, 330),
    # Cold-start niche winner: materially cheaper and stronger for coding/research.
    LatentProvider("newseed",   0.0012, {"coding":0.92,"research":0.89,"extraction":0.68,"fresh-search":0.70}, 560, 0.03, 50.0),
)


@dataclass(frozen=True)
class BuyerType:
    quality_weight: float
    price_weight: float
    latency_weight: float
    comparison_noise: float
    dishonest_probability: float = 0.0


DEFAULT_BUYER = BuyerType(quality_weight=1.0, price_weight=0.22, latency_weight=0.04, comparison_noise=0.035)


@dataclass
class SimResult:
    policy: str
    seed: int
    rounds: int
    mean_realized_quality: float
    mean_buyer_utility: float
    buyer_spend_usd: float
    research_spend_usd: float
    newseed_appearances: int
    newseed_purchases: int
    newseed_first_choices: int
    newseed_organic_purchases: int
    discovery_round: int | None
    evidence_bounties: int
    campaign_state: str
    avg_slate_k: float
    comparison_items: int
    reproducibility_hash: str


class ArenaSimulation:
    def __init__(self, *, seed: int, policy: str = "separated_ids", market=DEFAULT_MARKET,
                 cfg: MechanismConfig | None = None, buyer: BuyerType = DEFAULT_BUYER):
        self.seed = seed
        self.rng = random.Random(seed)
        self.policy_name = policy
        self.market = {p.provider_id: p for p in market}
        self.cfg = cfg or MechanismConfig()
        self.buyer = buyer
        self.beliefs = DiscountedContextualBeta(half_life_steps=700)
        self.campaigns = CampaignBook(self.cfg)
        self.coverage = CoverageBook()
        self.demand = DemandModel({"coding":1.0,"research":0.85,"extraction":0.75,"fresh-search":0.65})
        self.slate_policy = SeparatedSlatePolicy(self.beliefs, self.campaigns, self.demand, self.cfg, seed=seed)
        self.evidence_market = EvidenceMarket(self.coverage, lambda t,p: self.beliefs.uncertainty(t,p))
        self.events: list[dict] = []
        self.newseed_organic_enabled = False
        new = self.market.get("newseed")
        if new and new.sponsor_budget_usd > 0:
            self.campaigns.open(ProviderCampaign(
                campaign_id="campaign_newseed_v1", provider_id="newseed", version="1",
                funded_usd=new.sponsor_budget_usd, remaining_usd=new.sponsor_budget_usd,
            ))
        self._seed_incumbents()

    def _seed_incumbents(self):
        # Simulate pre-existing marketplace evidence. Cold-start provider intentionally receives none.
        for p in self.market.values():
            if p.provider_id == "newseed":
                continue
            for task in TASKS:
                for _ in range(12):
                    reward = min(1.0, max(0.0, p.qualities[task] + self.rng.gauss(0, 0.05)))
                    if self.rng.random() < p.failure_rate:
                        reward = 0.0
                    self.beliefs.update(task, p.provider_id, reward, weight=1.0)
                    self.coverage.add_evidence(task, p.provider_id, weight=1.0, created_at=1.0)

    def _task(self) -> str:
        xs = [("coding",0.32),("research",0.28),("extraction",0.22),("fresh-search",0.18)]
        x = self.rng.random(); c = 0.0
        for t,w in xs:
            c += w
            if x <= c: return t
        return xs[-1][0]

    def _provider_arms(self, task: str) -> list[ProviderArm]:
        arms = []
        for p in self.market.values():
            # All providers claim broad capability; latent quality determines whether claim is true.
            camp = self.campaigns.get_provider(p.provider_id)
            sponsor = camp.remaining_usd if camp else 0.0
            arms.append(ProviderArm(
                provider_id=p.provider_id, endpoint=f"https://{p.provider_id}.example/x402",
                price_usd=p.price_usd, task_tags=(task,"any"), schema_tags=("any",),
                healthy=True, version=p.version, sponsor_balance_usd=sponsor,
                metadata={"latency_ms":p.latency_ms,"success_prior":max(0.05,1-p.failure_rate)},
            ))
        return arms

    def _real_response_quality(self, provider_id: str, task: str) -> tuple[float, bool, float]:
        p = self.market[provider_id]
        failed = self.rng.random() < p.failure_rate
        q = 0.0 if failed else min(1.0, max(0.0, p.qualities[task] + self.rng.gauss(0, 0.045)))
        latency = max(50.0, p.latency_ms * math.exp(self.rng.gauss(0, 0.12)))
        return q, not failed, latency

    def _blind_score(self, provider_id: str, task: str) -> float:
        p = self.market[provider_id]
        q = p.qualities[task]
        # What the buyer can infer from a historical output, before seeing price/provider.
        return min(1.0, max(0.0, q + self.rng.gauss(0, self.buyer.comparison_noise)))

    def _economic_utility(self, provider_id: str, blind_score: float) -> float:
        p = self.market[provider_id]
        max_price = max(x.price_usd for x in self.market.values())
        return (self.buyer.quality_weight * blind_score
                - self.buyer.price_weight * (p.price_usd / max_price)
                - self.buyer.latency_weight * min(1.0, p.latency_ms / 2000.0))

    def _select_slate(self, ctx: RequestContext):
        arms = self._provider_arms(ctx.task)
        if self.policy_name == "organic_only":
            pool = self.slate_policy.score_pool(ctx, arms)
            k = self.slate_policy.adaptive_k(pool)
            chosen = sorted(pool, key=lambda c:c.organic_score, reverse=True)[:k]
            self.rng.shuffle(chosen)
            return chosen
        if self.policy_name == "random_explore":
            pool = self.slate_policy.score_pool(ctx, arms)
            k = self.slate_policy.adaptive_k(pool)
            leaders = sorted(pool,key=lambda c:c.organic_score, reverse=True)[:max(1,k-1)]
            left=[x for x in pool if x.provider_id not in {y.provider_id for y in leaders}]
            if left: leaders.append(self.rng.choice(left))
            self.rng.shuffle(leaders)
            return leaders
        if self.policy_name == "paid_rank_bad":
            pool = self.slate_policy.score_pool(ctx, arms)
            # Deliberately bad baseline: sponsor component corrupts recommendation score.
            k = self.slate_policy.adaptive_k(pool)
            chosen=sorted(pool,key=lambda c:c.organic_score+2.5*c.sponsor_component,reverse=True)[:k]
            self.rng.shuffle(chosen)
            return chosen
        if self.policy_name == "soft_research_auction":
            return self.slate_policy.choose_slate(ctx, arms, research_mode="soft_auction")
        return self.slate_policy.choose_slate(ctx, arms, research_mode="posted_price")

    def _maybe_seed_bounty(self, round_idx: int, ctx: RequestContext) -> int:
        c = self.campaigns.get_provider("newseed")
        if not c or c.state in {CampaignState.ELIMINATED, CampaignState.PAUSED, CampaignState.ORGANIC}:
            return 0
        # A brand-new provider has no historical output; commissioned purchase creates one.
        _, _, n = self.beliefs.stats(ctx.task, "newseed")
        if n >= 3:
            return 0
        p = self.market["newseed"]
        bounty = self.evidence_market.issue_bounty(
            request_id=ctx.request_id, task=ctx.task, provider_id="newseed", provider_cost_usd=p.price_usd,
            campaign_id=c.campaign_id, required_grade=EvidenceGrade.B_ARENA_OBSERVED,
        )
        if not bounty:
            return 0
        total = bounty.total_reward_usd
        if not self.campaigns.can_spend("newseed", total):
            return 0
        q, ok, latency = self._real_response_quality("newseed", ctx.task)
        self.campaigns.spend("newseed", total)
        self.beliefs.update(ctx.task, "newseed", q if ok else 0.0, weight=0.9)
        self.coverage.add_evidence(ctx.task, "newseed", weight=0.9)
        self.events.append({"round":round_idx,"kind":"bounty","task":ctx.task,"provider":"newseed","quality":q,"spend":total})
        return 1

    def run(self, rounds: int = 1500) -> SimResult:
        qualities=[]; utilities=[]; buyer_spend=0.0; research_spend_start=0.0
        new_apps=new_buys=new_first=new_org=0; discovery=None; bounties=0; total_k=0; compare_items=0
        c=self.campaigns.get_provider("newseed")
        if c: research_spend_start=c.spend_usd

        for r in range(1, rounds+1):
            self.beliefs.tick()
            task=self._task(); self.coverage.observe_demand(task)
            ctx=RequestContext(request_id=f"req-{self.seed}-{r}",text=f"{task} request {r}",task=task,budget_usd=0.02,buyer_id=f"buyer-{r%101}")
            if self.policy_name != "organic_only":
                bounties += self._maybe_seed_bounty(r,ctx)
            slate=self._select_slate(ctx)
            if not slate: continue
            total_k += len(slate); compare_items += len(slate)
            ids=[x.provider_id for x in slate]
            if "newseed" in ids: new_apps += 1
            c=self.campaigns.get_provider("newseed")
            if c and "newseed" in ids:
                self.campaigns.record_appearance("newseed",task,[x for x in ids if x!="newseed"])

            blind={pid:self._blind_score(pid,task) for pid in ids}
            # Consequential 5->2->1 tournament: buyer keeps two outputs it would actually investigate.
            ranked=sorted(ids,key=lambda p:blind[p],reverse=True)
            finalists=ranked[:min(2,len(ranked))]
            first=finalists[0]
            second=finalists[1] if len(finalists)>1 else None
            # After provider+price reveal, buyer may switch between finalists.
            buy=max(finalists,key=lambda p:self._economic_utility(p,blind[p]))
            if first=="newseed": new_first += 1
            if c and "newseed" in ids:
                beaten=[p for p in ids if p!="newseed" and blind["newseed"]>blind[p]]
                lost=[p for p in ids if p!="newseed" and blind["newseed"]<blind[p]]
                self.campaigns.record_feedback(
                    "newseed",task,finalist="newseed" in finalists,first=first=="newseed",
                    revealed="newseed" in finalists,purchased=buy=="newseed",worst=ranked[-1]=="newseed",
                    opponents_beaten=beaten,opponents_lost=lost,
                )
            exp=next((x for x in slate if x.provider_id=="newseed" and x.role=="experimental"),None)

            q,ok,lat=self._real_response_quality(buy,task)
            p=self.market[buy]
            buyer_spend += p.price_usd
            qualities.append(q)
            u=q-self.buyer.price_weight*(p.price_usd/max(x.price_usd for x in self.market.values()))
            utilities.append(u)
            # Actual purchase/outcome is strongest signal.
            self.beliefs.update(task,buy,q if ok else 0.0,weight=1.0)
            self.coverage.add_evidence(task,buy,weight=1.0)
            if buy=="newseed":
                new_buys += 1
                if not exp: new_org += 1
                if c: self.campaigns.record_feedback("newseed",task,purchased=True,success=ok)
            self.events.append({"round":r,"task":task,"slate":ids,"first":first,"finalists":finalists,"buy":buy,"quality":round(q,6),"price":p.price_usd})

            # Define discovery as posterior lower evidence + organic eligibility, not one lucky win.
            if discovery is None:
                means=[]
                for t in ("coding","research"):
                    m,v,n=self.beliefs.stats(t,"newseed"); means.append((m,n))
                if all(n>=8 and m>=0.80 for m,n in means):
                    discovery=r; self.newseed_organic_enabled=True

        c=self.campaigns.get_provider("newseed")
        payload=json.dumps(self.events,sort_keys=True,separators=(",",":"))
        return SimResult(
            policy=self.policy_name,seed=self.seed,rounds=rounds,
            mean_realized_quality=sum(qualities)/len(qualities) if qualities else 0.0,
            mean_buyer_utility=sum(utilities)/len(utilities) if utilities else 0.0,
            buyer_spend_usd=buyer_spend,
            research_spend_usd=(c.spend_usd-research_spend_start) if c else 0.0,
            newseed_appearances=new_apps,newseed_purchases=new_buys,newseed_first_choices=new_first,
            newseed_organic_purchases=new_org,discovery_round=discovery,evidence_bounties=bounties,
            campaign_state=c.state.value if c else "NONE",avg_slate_k=total_k/max(1,rounds),comparison_items=compare_items,
            reproducibility_hash=sha256(payload.encode()).hexdigest(),
        )
