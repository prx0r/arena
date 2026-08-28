from __future__ import annotations
import json
from pathlib import Path


TASK_FILE_BY_TYPE = {"T1":"humaneval.jsonl", "T2":"hotpotqa.jsonl", "T3a":"triviaqa.jsonl", "T3b":"openweb.jsonl"}


def _load_tasks(root: Path) -> dict[str, str]:
    result={}
    for fp in root.glob("*.jsonl"):
        for line in fp.read_text(errors="ignore").splitlines():
            if not line.strip(): continue
            d=json.loads(line)
            tid=d.get("task_id") or d.get("id")
            text=d.get("prompt") or d.get("question") or d.get("input") or d.get("query") or d.get("text")
            if tid and text: result[str(tid)]=str(text)
    return result


def load_402pilot(repo_root: str | Path) -> list[dict]:
    root=Path(repo_root)
    tasks=_load_tasks(root/"data"/"tasks")
    rows=[]
    for fp in sorted((root/"data"/"pregen").glob("*.jsonl")):
        for line in fp.read_text(errors="ignore").splitlines():
            if not line.strip(): continue
            d=json.loads(line)
            q=d.get("quality_score",{}).get("q")
            rows.append({
                "task_id": d["task_id"], "task_type": d["task_type"], "task_text": tasks.get(d["task_id"], d["task_id"]),
                "provider_id": d["provider_id"], "version": int(d.get("version",0)), "response": d.get("response",""),
                "cost_usd": float(d.get("cost_usdc",0)), "latency_ms": 1000*float(d.get("latency_s",0)),
                "quality": 0.0 if q is None else float(q), "failed": bool(d.get("failure_flag",False)),
                "generated_at": d.get("generated_at","")
            })
    return rows
