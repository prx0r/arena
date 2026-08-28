from arena402.replay import ReplayMarket, run_policy
from arena402.policies.baselines import Cheapest
from arena402.policies.padct import PADCT

ROWS=[]
for task,typ in [("t1","code"),("t2","qa")]:
    for p,c,q in [("cheap",0.001,0.5),("good",0.004,0.95)]:
        for v in range(5): ROWS.append({"task_id":task,"task_type":typ,"task_text":task,"provider_id":p,"version":v,"response":"x","cost_usd":c,"latency_ms":10,"quality":q,"failed":False})


def test_replay_runs():
    m=ReplayMarket(ROWS)
    r=run_policy(ROWS,Cheapest(m.prices),rounds=100)
    assert r["rounds"]==100 and r["spend_usd"]>0


def test_padct_runs():
    m=ReplayMarket(ROWS)
    r=run_policy(ROWS,PADCT(m.prices,budget=1,horizon=100),rounds=100)
    assert 0 <= r["mean_quality"] <= 1
