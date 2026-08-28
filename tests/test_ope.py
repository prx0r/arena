from arena402.ope import ips, snips, doubly_robust

def test_ope_estimators():
    rows=[{"reward":1.0,"target_prob":0.5,"logging_prob":0.5,"q_target":0.8,"q_logged":0.8},
          {"reward":0.0,"target_prob":0.5,"logging_prob":0.5,"q_target":0.2,"q_logged":0.2}]
    assert abs(ips(rows)-0.5)<1e-9
    assert abs(snips(rows)-0.5)<1e-9
    assert 0 <= doubly_robust(rows) <= 1
