from __future__ import annotations

"""Fetch the public 402Pilot benchmark files from GitHub.

402Pilot's README states its frozen replay has 823 tasks x 5 providers x 5
versions = 20,575 records. Its repository license permits research/educational
use; check the upstream LICENSE before commercial redistribution.
"""

import argparse
from pathlib import Path
from urllib.request import urlopen

BASE="https://raw.githubusercontent.com/MCCodeAI/402Pilot/main"
PROVIDERS=["P-cheap","P-mid","P-premium","P-adv","P-flaky"]
TASK_TYPES=["T1","T2","T3a","T3b"]
TASK_FILES=["humaneval.jsonl","hotpotqa.jsonl","triviaqa.jsonl","openweb.jsonl"]


def get(url: str, path: Path):
    path.parent.mkdir(parents=True,exist_ok=True)
    print(f"GET {url} -> {path}")
    with urlopen(url,timeout=60) as r, path.open("wb") as f:
        f.write(r.read())


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",default="external/402Pilot")
    a=ap.parse_args(); root=Path(a.out)
    for fn in TASK_FILES: get(f"{BASE}/data/tasks/{fn}",root/"data"/"tasks"/fn)
    for p in PROVIDERS:
        for t in TASK_TYPES:
            fn=f"{p}__{t}.jsonl"; get(f"{BASE}/data/pregen/{fn}",root/"data"/"pregen"/fn)
    get(f"{BASE}/LICENSE",root/"LICENSE")
    get(f"{BASE}/data/ATTRIBUTION.md",root/"data"/"ATTRIBUTION.md")
    print("Done. Run: python scripts/run_402pilot_experiments.py --repo",root)

if __name__=="__main__": main()
