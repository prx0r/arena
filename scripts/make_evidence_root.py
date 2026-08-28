from __future__ import annotations
import argparse, json
from arena402.merkle import merkle_root

p=argparse.ArgumentParser(); p.add_argument("jsonl"); a=p.parse_args()
rows=[line.rstrip("\n").encode() for line in open(a.jsonl,"rb") if line.strip()]
print(json.dumps({"count":len(rows),"root":merkle_root(rows)},indent=2))
