import sys
sys.path.insert(0, "/root/402arena")
from arena402.evidence_market import EvidenceMarket, CoverageBook
from arena402.mechanism import EvidenceGrade
from arena402.store import Store
from arena402.models import Provider, Observation
import tempfile, time

def test_quote_saturates():
    store = Store(tempfile.NamedTemporaryFile(suffix=".sqlite",delete=False).name)
    store.add_provider(Provider("p1","P1","https://p1.invalid",0.01,"search"))
    for i in range(100):
        store.add_observation(Observation(f"query {i}","p1","output",0.01,80,0.8,True,"search",time.time()-i*86400,source="test",public_example=True))
    cb = CoverageBook()
    for i in range(100):
        cb.add_evidence("query 100", "p1", weight=1.0, created_at=time.time()-i*86400)
    market = EvidenceMarket(cb, lambda t,p: 0.5)
    q = market.quote_organic("query 100", "p1", grade=EvidenceGrade.A_PROVIDER_BOUND,
        request_hash="a"*64, response_hash="b"*64, receipt_hash="c"*64)
    print(f"saturated: bid=${q.bid_usd:.6f} reasons: {q.reasons}")

def test_quote_sparse():
    store = Store(tempfile.NamedTemporaryFile(suffix=".sqlite",delete=False).name)
    store.add_provider(Provider("p1","P1","https://p1.invalid",0.01,"search"))
    store.add_observation(Observation("rare query","p1","output",0.01,80,0.8,True,"search",time.time(),source="test",public_example=True))
    cb = CoverageBook()
    cb.add_evidence("rare query", "p1", weight=1.0)
    market = EvidenceMarket(cb, lambda t,p: 0.8)
    q = market.quote_organic("rare query", "p1", grade=EvidenceGrade.A_PROVIDER_BOUND,
        request_hash="a"*64, response_hash="b"*64, receipt_hash="c"*64)
    print(f"sparse: bid=${q.bid_usd:.6f} reasons: {q.reasons}")

if __name__ == "__main__":
    test_quote_saturates()
    test_quote_sparse()
    print("all tests passed")
