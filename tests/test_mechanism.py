from arena402.bandits import DiscountedContextualBeta
from arena402.choice import validate_tournament
from arena402.evidence_market import CoverageBook, EvidenceMarket
from arena402.ledger import SimEscrow
from arena402.mechanism import EvidenceGrade, MechanismConfig, ProviderCampaign
from arena402.merkle import merkle_root
from arena402.sepolia import BASE_MAINNET, BASE_SEPOLIA
from arena402.simulation import ArenaSimulation
from arena402.sponsor import CampaignBook


def test_base_network_constants():
    assert BASE_SEPOLIA.chain_id==84532
    assert BASE_SEPOLIA.caip2=="eip155:84532"
    assert BASE_SEPOLIA.usdc_address.lower()=="0x036cbd53842c5426634e7929541ec2318f3dcf7e".lower()
    assert BASE_MAINNET.chain_id==8453


def test_tournament_yields_partial_not_full_ranking():
    r=validate_tournament(["a","b","c","d","e"],["b","e"],["e","b"])
    assert r.partial_order()==(("e",),("b",),("a","c","d"))
    # e beats b+a+c+d; b beats a+c+d => 7 defensible edges, no ordering among losers.
    assert len(r.pairwise())==7


def test_adaptive_k_moves_with_uncertainty():
    from arena402.slate import DemandModel, SeparatedSlatePolicy
    from arena402.mechanism import ProviderArm, RequestContext
    camp=CampaignBook(); beliefs=DiscountedContextualBeta()
    policy=SeparatedSlatePolicy(beliefs,camp,DemandModel({"coding":1.0}),MechanismConfig(min_k=3,max_k=8))
    ctx=RequestContext("r","x","coding",0.1)
    providers=[ProviderArm(str(i),f"https://{i}",0.001,("coding",),metadata={"success_prior":0.8}) for i in range(8)]
    high=policy.adaptive_k(policy.score_pool(ctx,providers))
    for p in providers:
        for _ in range(80): beliefs.update("coding",p.provider_id,0.8)
    low=policy.adaptive_k(policy.score_pool(ctx,providers))
    assert high>=low


def test_sponsor_money_does_not_change_organic_score():
    from arena402.slate import DemandModel, SeparatedSlatePolicy
    from arena402.mechanism import ProviderArm, RequestContext
    cfg=MechanismConfig(); camp=CampaignBook(cfg); beliefs=DiscountedContextualBeta()
    p=ProviderArm("new","https://new",0.001,("coding",),metadata={"success_prior":0.8})
    ctx=RequestContext("r","x","coding",0.1)
    policy=SeparatedSlatePolicy(beliefs,camp,DemandModel({"coding":1.0}),cfg)
    before=policy.score_pool(ctx,[p])[0].organic_score
    camp.open(ProviderCampaign("c","new","1",1000,1000))
    after=policy.score_pool(ctx,[p])[0]
    assert before==after.organic_score
    assert after.sponsor_component>0


def test_evidence_market_saturates():
    beliefs=DiscountedContextualBeta(); coverage=CoverageBook(); market=EvidenceMarket(coverage,lambda t,p:beliefs.uncertainty(t,p))
    coverage.observe_demand("coding",100)
    q1=market.quote_organic("coding","p",grade=EvidenceGrade.B_ARENA_OBSERVED,request_hash="r1",response_hash="s1",receipt_hash="t1")
    for _ in range(500): coverage.add_evidence("coding","p",weight=1)
    for _ in range(200): beliefs.update("coding","p",0.8)
    q2=market.quote_organic("coding","p",grade=EvidenceGrade.B_ARENA_OBSERVED,request_hash="r2",response_hash="s2",receipt_hash="t2")
    assert q2.bid_usd < q1.bid_usd


def test_escrow_conservation_and_replay_protection():
    e=SimEscrow(); e.fund("c","owner",10_000_000); e.pay("c","b1",2_000_000); e.refund("c","owner",1_000_000)
    assert e.invariant()
    try: e.pay("c","b1",1)
    except ValueError: pass
    else: raise AssertionError("replay accepted")


def test_merkle_root_deterministic():
    rows=[b"a",b"b",b"c"]
    assert merkle_root(rows)==merkle_root(rows)
    assert merkle_root(rows)!=merkle_root(list(reversed(rows)))


def test_simulation_is_byte_reproducible():
    a=ArenaSimulation(seed=42,policy="separated_ids").run(200)
    b=ArenaSimulation(seed=42,policy="separated_ids").run(200)
    assert a.reproducibility_hash==b.reproducibility_hash
    assert a==b
