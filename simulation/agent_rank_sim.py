"""
Agent ranking simulator — tests how agents rank under scarce vs full reveals.
Uses 402Arena-cg logic but with synthetic agent policies (33 styles) as stand-ins for real LLM agents.
Logs every trial as JSONL receipt for Cogym evolution. Chain-agnostic for now.
"""
import json, time, random, pathlib
from collections import defaultdict

# Mock agent policies: 33 styles simplified to 5 archetypes for simulation
AGENT_ARCHETYPES = ["greedy","cautious","anxious","reckless","analytical"]
# Each archetype has different bias in picking best/worst

def synthetic_agent_choose(slate, archetype, reveal_mode="scarce"):
    """
    slate: list of items with similarity, quality, cost
    reveal_mode: "scarce" (2 reveals) vs "full" (all reveal)
    Returns: (best_blind, worst_blind, purchase_blind or None)
    """
    # Agent scores items differently per archetype
    weights = {
        "greedy": (0.5, 0.1, 0.4), # favors cheap
        "cautious": (0.7, 0.2, 0.1), # favors similarity+quality
        "anxious": (0.4, 0.4, 0.2),
        "reckless": (0.3, 0.1, 0.6), # cheap + random
        "analytical": (0.6, 0.3, 0.1),
    }[archetype]
    scored = []
    for it in slate:
        sim, qual, cost = it["similarity"], it.get("evidence_quality",0.5), it["cost_usd"]
        # normalize cost inverse
        score = weights[0]*sim + weights[1]*(qual or 0.5) - weights[2]*cost*10
        # add noise per archetype
        score += random.gauss(0, 0.05 if archetype=="analytical" else 0.15)
        scored.append((score, it))
    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1]["blind_id"]
    worst = scored[-1][1]["blind_id"]
    # Purchase decision: after reveal, check price sensitivity
    # In scarce mode, only best/worst revealed, so purchase is best if price low else second
    if reveal_mode=="scarce":
        # scarce: agent only sees best/worst provider+price, picks cheaper if quality close
        purchase = best if scored[0][0] - scored[1][0] > 0.1 else (scored[1][1]["blind_id"] if scored[1][1]["cost_usd"] < scored[0][1]["cost_usd"]*0.7 else best)
    else:
        # full reveal: agent sees all, picks best quality/price tradeoff
        purchase = best
    return best, worst, purchase

def run_batch(n_trials=100, reveal_mode="scarce", log_path="logs/rank_sim.jsonl"):
    log_path = pathlib.Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    results = defaultdict(list)
    for i in range(n_trials):
        # synthetic slate: 5 items with varying sim/qual/cost
        slate = [
            {"blind_id": f"b{j}", "similarity": random.uniform(0.7,0.95), "evidence_quality": random.uniform(0.6,0.95), "cost_usd": random.uniform(0.001,0.02), "provider_id": f"p{j}"}
            for j in range(5)
        ]
        for arch in AGENT_ARCHETYPES:
            best, worst, purchase = synthetic_agent_choose(slate, arch, reveal_mode)
            # Log receipt
            receipt = {
                "trial": i, "arch": arch, "reveal_mode": reveal_mode,
                "slate": slate, "best": best, "worst": worst, "purchase": purchase,
                "ts": time.time(), "run_id": f"sim_{reveal_mode}_{arch}_{i}"
            }
            with open(log_path, "a") as f:
                f.write(json.dumps(receipt)+"\n")
            results[arch].append((best,worst))
    print(f"logged {n_trials*len(AGENT_ARCHETYPES)} receipts to {log_path} mode={reveal_mode}")
    # summary
    for arch, vals in results.items():
        print(f"{arch}: best distribution {Counter(v[0] for v in vals)}")
    return log_path

if __name__ == "__main__":
    from collections import Counter
    run_batch(50, "scarce", "/root/402arena/logs/rank_sim_scarce.jsonl")
    run_batch(50, "full", "/root/402arena/logs/rank_sim_full.jsonl")
