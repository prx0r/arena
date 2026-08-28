from __future__ import annotations
import argparse, json
from .store import Store
from .service import ArenaService


def main():
    p=argparse.ArgumentParser(prog="402arena")
    p.add_argument("--db",default="arena402.sqlite")
    s=p.add_subparsers(dest="cmd",required=True)
    r=s.add_parser("recommend"); r.add_argument("query"); r.add_argument("--top",type=int,default=5)
    c=s.add_parser("choose"); c.add_argument("slate_id"); c.add_argument("blind_id")
    f=s.add_parser("fund"); f.add_argument("provider_id"); f.add_argument("amount",type=float)
    a=p.parse_args(); store=Store(a.db); svc=ArenaService(store)
    if a.cmd=="recommend": out=svc.recommend(a.query,a.top)
    elif a.cmd=="choose": out=svc.choose(a.slate_id,a.blind_id)
    else: store.fund_provider(a.provider_id,a.amount); out={"ok":True}
    print(json.dumps(out,indent=2,default=str))

if __name__=="__main__": main()
