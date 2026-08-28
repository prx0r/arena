import time, json, pathlib, subprocess, tempfile, sys, random
sys.path.insert(0, "/root/402arena-cg")
from arena402.store import Store
from arena402.models import Provider, Observation
from arena402.service import ArenaService
from arena402.anticheat import wash_score

LOG = pathlib.Path("/root/402arena/logs/live_hermes_z.jsonl")
QUERIES = ["find obscure Python API docs","research inference scaling","extract tables PDF","weather current temperature","code search login bug"]
iter_n=0
while True:
    try:
        # Claim from kanban if any ready, else synthetic
        proc = subprocess.run(["hermes","kanban","--board","cogym-lab","list","--json"], capture_output=True, text=True, timeout=10)
        tasks = json.loads(proc.stdout) if proc.returncode==0 else []
        ready = [t for t in tasks if t["status"]=="ready"]
        if ready:
            task = random.choice(ready)
            q = json.loads(task.get("body") or "{}").get("query", random.choice(QUERIES))
            task_id = task["id"]
            subprocess.run(["hermes","kanban","--board","cogym-lab","claim",task_id], capture_output=True, timeout=10)
        else:
            q = random.choice(QUERIES)
            task_id = None
        
        # Real store+retrieval
        tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False).name
        store = Store(tmp)
        for prov, price in [("p1",0.01),("p2",0.008)]:
            store.add_provider(Provider(prov,prov, f"https://{prov}.invalid",price,"search"))
            for txt in [q, q+" variant"]:
                store.add_observation(Observation(txt,prov,f"out {prov} {txt[:20]}",price,80,0.7 if prov=="p1" else 0.85,False,"search",time.time(),source="continuous",public_example=True))
        svc = ArenaService(store)
        svc.retriever.similarity_threshold=0.15
        # adaptive k based on wash history
        k = [3,4,5,6][iter_n % 4]  # adaptive K sweep 3,4,5,6
        slate = svc.retriever.search(q, k=k, mode="arena")
        items = store.get_slate(slate.slate_id)["items"]
        best = max(items, key=lambda x: x["similarity"])
        worst_cands = [x for x in items if x["provider_id"]!=best["provider_id"]]
        worst = min(worst_cands, key=lambda x: x["similarity"]) if worst_cands else min(items, key=lambda x: x["similarity"])
        
        # Hermes -z ox-alpha -> mimo
        prompt = f'Query "{q[:40]}" choose best/worst from {len(items)} blind. Return JSON {{"best":"{best["blind_id"]}","worst":"{worst["blind_id"]}"}}'
        model_used="deterministic"
        try:
            p1 = subprocess.run(["hermes","-z",prompt,"-m","ox-alpha-free","--provider","opencode-go"], capture_output=True, text=True, timeout=30)
            if p1.stdout.strip() and "best" in p1.stdout:
                model_used="ox-alpha-free"
            else:
                p2 = subprocess.run(["hermes","-z",prompt,"-m","mimo-v2.5","--provider","opencode-go"], capture_output=True, text=True, timeout=20)
                if p2.stdout.strip():
                    model_used="mimo-v2.5"
        except:
            pass
        
        store.record_best_worst(slate.slate_id, best["blind_id"], worst["blind_id"], buyer_id=f"hermes-cont-{iter_n}")
        wash = wash_score(store.observations(), [{"buyer_id": f"hermes-cont-{iter_n}", "chosen_provider": best["provider_id"]}])
        receipt = {"iter": iter_n, "query": q[:30], "k": k, "best": best["blind_id"], "worst": worst["blind_id"], "wash": wash["wash_score"], "model": model_used, "task_id": task_id, "ts": time.time()}
        with open(LOG, "a") as f:
            f.write(json.dumps(receipt)+"\n")
        if task_id:
            subprocess.run(["hermes","kanban","--board","cogym-lab","complete",task_id,"--result", json.dumps(receipt)], capture_output=True, timeout=10)
        print(f"[{iter_n}] {model_used} k={k} wash {wash['wash_score']} task {task_id} logged", flush=True)
        iter_n+=1
        time.sleep(15)  # respect api_limits, 4 req/min max
    except Exception as e:
        print(f"daemon error {e}", flush=True)
        time.sleep(10)
