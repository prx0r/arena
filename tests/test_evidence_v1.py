import sys
sys.path.insert(0, "/root/402arena")
from arena402.x402 import ArenaEvidenceV1
import hashlib

def test_arena_evidence_v1_create():
    e = ArenaEvidenceV1.create(
        "https://newsearch.invalid/search", "0xBuyer", "newsearch",
        "find Python docs", "output from newsearch", "3000", "0xTxHash123"
    )
    assert e.requestHash == hashlib.sha256(b"find Python docs").hexdigest()
    assert e.responseHash == hashlib.sha256(b"output from newsearch").hexdigest()
    assert e.network == "eip155:84532"
    assert e.amount == "3000"
    assert e.provider == "newsearch"
    assert len(e.providerSignature) == 64  # sha256 hex

def test_arena_evidence_v1_verify():
    e = ArenaEvidenceV1.create("https://p.invalid", "0xB", "p", "req", "resp", "1000", "0xTx")
    # Recompute hashes
    assert e.requestHash == hashlib.sha256(b"req").hexdigest()
    assert e.responseHash == hashlib.sha256(b"resp").hexdigest()

def test_grade_weights():
    from arena402.mechanism import GRADE_WEIGHT, EvidenceGrade
    assert GRADE_WEIGHT[EvidenceGrade.A_PROVIDER_BOUND] == 1.00
    assert GRADE_WEIGHT[EvidenceGrade.B_ARENA_OBSERVED] == 0.90
    assert GRADE_WEIGHT[EvidenceGrade.C_BUYER_ATTESTED] == 0.55
    assert GRADE_WEIGHT[EvidenceGrade.D_UNVERIFIED] == 0.15

if __name__ == "__main__":
    test_arena_evidence_v1_create()
    test_arena_evidence_v1_verify()
    test_grade_weights()
    print("all tests passed")
