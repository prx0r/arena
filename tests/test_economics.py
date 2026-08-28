from arena402.economics import inject_new_provider, SeededExplorer
from arena402.replay import ReplayMarket, run_policy

ROWS=[]
for task,typ in [("t1","code"),("t2","qa")]:
    for p,c,q in [("cheap",0.001,0.5),("premium",0.01,0.95)]:
        for v in range(3): ROWS.append({"task_id":task,"task_type":typ,"task_text":task,"provider_id":p,"version":v,"response":"x","cost_usd":c,"latency_ms":10,"quality":q,"failed":False})

def test_cold_start_injection_and_budget():
    rows=inject_new_provider(ROWS,source_provider="premium",new_provider="new",price_usd=0.002)
    m=ReplayMarket(rows)
    assert "new" in m.providers
    p=SeededExplorer(m.prices,1.0,seed=1)
    r=run_policy(rows,p,rounds=100,seed=1)
    assert r["rounds"]==100
    assert p.subsidy_spend <= 1.0 + 1e-9
