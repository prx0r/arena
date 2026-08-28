from __future__ import annotations
import argparse, time
from arena402.datasets import load_402pilot
from arena402.models import Provider, Observation
from arena402.store import Store


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",required=True); ap.add_argument("--db",default="arena402.sqlite"); ap.add_argument("--limit",type=int,default=0)
    a=ap.parse_args(); rows=load_402pilot(a.repo); store=Store(a.db)
    prices={p:min(x["cost_usd"] for x in rows if x["provider_id"]==p) for p in sorted({x["provider_id"] for x in rows})}
    for p,price in prices.items(): store.add_provider(Provider(p,p,f"replay://402pilot/{p}",price_usd=price,category="llm"))
    for i,r in enumerate(rows[:a.limit or None]):
        store.add_observation(Observation(
            request_text=r["task_text"],provider_id=r["provider_id"],response_preview=r["response"][:1200],
            cost_usd=r["cost_usd"],latency_ms=r["latency_ms"],quality=r["quality"],success=not r["failed"],
            task_type=r["task_type"],created_at=time.time()-((len(rows)-i)%90)*86400,
            source="402pilot",public_example=True,
        ))
    print(f"loaded {min(len(rows),a.limit or len(rows))} observations into {a.db}")

if __name__=="__main__": main()
