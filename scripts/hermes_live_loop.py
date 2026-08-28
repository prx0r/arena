"""Hermes live loop — each Hermes worker = agent with query choosing blind options.
Uses ox-alpha-free via `hermes -z`, logs every receipt. Chain-agnostic, Base Sepolia ready."""
import json, time, subprocess, pathlib, sys, tempfile, random
sys.path.insert(0, "/root/402arena-cg")
from arena402.store import Store
from arena402.models import Provider, Observation
from arena402.service import ArenaService

LOG = pathlib.Path("/root/402arena/logs/live_hermes_z.jsonl")
LOG.parent.mkdir(parents=True, exist_ok=True)

def hermes_choose_ox_alpha(slate, query):
    """Call hermes -z ox-alpha-free to pick best/worst. Fallback to deterministic if timeout."""
    prompt = f"""You are an agent choosing blind historical outputs for query: "{query}"

Slate (5 blind, provider hidden):
{json.dumps([{'id': it['blind_id'], 'sim': it['similarity'], 'preview': it['output_preview'][:120], 'cost': it['cost_usd']} for it in slate], indent=2)}

Pick BEST and WORST blind_id. Return JSON only: {{"best":"...","worst":"...","reason":"..."}}"""
    try:
        # use hermes -z with ox-alpha-free, JSON output
        proc = subprocess.run(
            ["hermes", "-z", prompt, "-m", "ox-alpha-free", "--provider", "opencode-go"  # primary
            # fallback to mimo-v2.5 if empty (implemented below)],
            capture_output=True, text=True, timeout=45
        )
        out = proc.stdout.strip()
        if not out or "No reply" in out:
            # fallback 1: muse-spark-1.2
            proc2 = subprocess.run(
                ["hermes", "-z", prompt, "-m", "muse-spark-1.2", "--provider", "opencode-go"],
                capture_output=True, text=True, timeout=30
            )
            out = proc2.stdout.strip()
        if not out or "No reply" in out:
            # fallback 2: mimo-v2.5
            proc3 = subprocess.run(
                ["hermes", "-z", prompt, "-m", "mimo-v2.5", "--provider", "opencode-go"],
                capture_output=True, text=True, timeout=30
            )
            out = proc3.stdout.strip()
        # extract JSON
        import re
        m = re.search(r"\{.*?\}", out, re.DOTALL)
        if m:
            j = json.loads(m.group(0))
            return j.get("best"), j.get("worst")
    except Exception as e:
        print(f"hermes -z fallback: {e}")
    # fallback deterministic: best = max sim, worst = min sim
    best = max(slate, key=lambda x: x["similarity"])["blind_id"]
    worst = min(slate, key=lambda x: x["similarity"])["blind_id"]
    return best, worst

def run_one(query="find obscure Python API docs"):
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False).name
    store = Store(tmp)
    store.add_provider(Provider("cheap","Cheap","https://c.invalid",0.001,"search"))
    store.add_provider(Provider("specialist","Specialist","https://s.invalid",0.008,"search"))
    for q, p, qual in [(query,"cheap",0.6),(query,"specialist",0.9)]:
        store.add_observation(Observation(q,p,f"output {p}",0.001 if p=="cheap" else 0.008,80,qual,False,"search",time.time(),source="hermes-z",public_example=True))
    svc = ArenaService(store)
    svc.retriever.similarity_threshold = 0.15
    # scarce 2-reveal: k=5 arena mode
    slate = svc.retriever.search(query, k=5, mode="arena")
    if len(slate.items) < 2:
        print(f"slate too small {len(slate.items)}")
        return
    slate_dicts = [dict(b.__dict__, provider_id=hid["provider_id"]) for b, hid in zip(slate.items, store.get_slate(slate.slate_id)["items"])]
    # Hermes ox-alpha choice
    best, worst = hermes_choose_ox_alpha([{"blind_id": d["blind_id"], "similarity": d["similarity"], "output_preview": d["historical_request"], "cost_usd": d["cost_usd"]} for d in slate_dicts], query)
    if best not in [d["blind_id"] for d in slate_dicts]:
        best = slate_dicts[0]["blind_id"]
    if worst not in [d["blind_id"] for d in slate_dicts] or worst==best:
        worst = slate_dicts[-1]["blind_id"]
    store.record_best_worst(slate.slate_id, best, worst, buyer_id="hermes-ox-alpha")
    receipt = {"run_id": slate.slate_id, "query": query, "best": best, "worst": worst, "k": 5, "mode": "arena", "model": "ox-alpha-free", "ts": time.time()}
    with open(LOG, "a") as f:
        f.write(json.dumps(receipt)+"\n")
    print(f"logged {receipt} to {LOG} | provenance {store.get_provenance(slate.slate_id)[:1]}")
    return receipt

if __name__ == "__main__":
    for q in ["find obscure Python API docs","research inference scaling"][:2]:
        run_one(q)
