import tempfile, time
from arena402.models import Provider, Observation
from arena402.store import Store
from arena402.service import ArenaService


def make_store():
    p=tempfile.NamedTemporaryFile(suffix=".sqlite",delete=False).name
    s=Store(p)
    s.add_provider(Provider("a","A","https://a.invalid",0.01,"search"))
    s.add_provider(Provider("b","B","https://b.invalid",0.005,"search"))
    s.add_observation(Observation("python documentation search","a","docs A",0.01,100,0.8,True,"search",time.time(),source="test",public_example=True))
    s.add_observation(Observation("python library API docs","b","docs B",0.005,80,0.95,True,"search",time.time(),source="test",public_example=True))
    return s


def test_blind_recommend_then_reveal_does_not_invent_pairwise_edges():
    s=make_store(); svc=ArenaService(s)
    r=svc.recommend("find python API documentation",2)
    assert len(r["items"])==2
    assert all("provider_id" not in x for x in r["items"])
    chosen=svc.choose(r["slate_id"],r["items"][0]["blind_id"],"buyer")
    assert chosen["provider"]["provider_id"] in {"a","b"}
    assert s.pairwise_counts()==[]


def test_consequential_tournament_records_only_supported_partial_order():
    s=make_store(); svc=ArenaService(s)
    r=svc.recommend("find python API documentation",2)
    ids=[x["blind_id"] for x in r["items"]]
    out=svc.commit_tournament(r["slate_id"],ids[:2],[ids[0],ids[1]],"buyer")
    assert out["pairwise_edges_recorded"]==1
    assert len(s.pairwise_counts())==1


def test_sponsor_fund_does_not_enter_recommendation():
    s=make_store(); svc=ArenaService(s)
    before=[x["observation_id"] for x in svc.recommend("find python API documentation",2)["items"]]
    s.fund_provider("a",1000)
    after=[x["observation_id"] for x in svc.recommend("find python API documentation",2)["items"]]
    assert before==after


def test_research_credit_exists_for_funded_provider():
    s=make_store(); svc=ArenaService(s); s.fund_provider("a",10)
    offer=svc.research_offer("rare legal extraction problem","a")
    assert offer is not None
    assert offer["buyer_price_usd"] <= offer["normal_price_usd"]
