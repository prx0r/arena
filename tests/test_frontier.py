from arena402.preferences_v2 import ContextualBradleyTerry, ContextualPlackettLuce
from arena402.ope import slate_ips, switch_dr, diagnostics
from arena402.research_market import ResearchCandidate, ResearchSlotMarket
from arena402.mechanism import ProviderCampaign
from arena402.provider_report import build_provider_report


def test_contextual_bt_is_task_specific():
    m=ContextualBradleyTerry(lr=0.1)
    for _ in range(100): m.update("coding","new","old")
    for _ in range(100): m.update("news","old","new")
    assert m.win_prob("coding","new","old") > 0.7
    assert m.win_prob("news","new","old") < 0.3


def test_partial_order_does_not_invent_ties():
    m=ContextualBradleyTerry(lr=0.05)
    n=m.update_partial_order("coding",[["e"],["b"],["a","c","d"]])
    assert n==7
    assert abs(m.win_prob("coding","a","c") - 0.5) < 0.01


def test_plackett_luce_commissioned_ranking():
    m=ContextualPlackettLuce()
    for _ in range(80):m.update_ranking("coding",["a","b","c"])
    r=[p for p,_ in m.ranking("coding",["a","b","c"])]
    assert r==["a","b","c"]


def test_slate_ope_and_diagnostics():
    rows=[
        {"reward":1.0,"logging_item_probs":[0.5,0.5],"target_item_probs":[0.5,0.5]},
        {"reward":0.0,"logging_item_probs":[0.5,0.5],"target_item_probs":[0.5,0.5]},
    ]
    assert abs(slate_ips(rows)-0.5)<1e-9
    base=[{"reward":1,"logging_prob":0.5,"target_prob":0.5,"q_target":0.7,"q_logged":0.7}]
    assert 0<=switch_dr(base)<=1
    assert diagnostics(base).effective_n>0


def test_research_money_cannot_override_eligibility():
    market=ResearchSlotMarket(seed=1)
    irrelevant=ResearchCandidate("rich",0.1,1.0,1.0,1000,1.0,explicit_bid_usd=1000)
    good=ResearchCandidate("good",0.9,0.8,1.0,1,1.0,explicit_bid_usd=0.002)
    out=market.allocate_soft_auction([irrelevant,good])
    assert out and out.provider_id=="good"


def test_posted_price_increases_as_trials_become_less_valuable():
    market=ResearchSlotMarket()
    early=ResearchCandidate("p",0.9,0.8,1.0,10,1.0)
    late=ResearchCandidate("p",0.9,0.2,1.0,10,4.0)
    assert market.posted_price(late)>market.posted_price(early)


def test_provider_report_exposes_funnel_without_raw_request():
    c=ProviderCampaign("c","p","1",10,7,blind_appearances=20,first_choice_count=8,purchases=5,spend_usd=3)
    r=build_provider_report(c,[])
    assert r["funnel"]["first_choice_rate"]==0.4
    assert "privacy_note" in r
