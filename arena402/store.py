from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Iterable

from .embedding import HashingEmbedder
from .models import Observation, Provider


SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS providers(
  provider_id TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  price_usd REAL NOT NULL,
  category TEXT NOT NULL,
  endpoint_fingerprint TEXT NOT NULL,
  metadata_json TEXT NOT NULL,
  capability_family TEXT NOT NULL DEFAULT '',
  upstream_family TEXT NOT NULL DEFAULT '',
  pipeline_fingerprint TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS observations(
  observation_id TEXT PRIMARY KEY,
  request_id TEXT NOT NULL,
  request_text TEXT NOT NULL,
  request_vec_json TEXT NOT NULL,
  provider_id TEXT NOT NULL,
  response_preview TEXT NOT NULL,
  cost_usd REAL NOT NULL,
  latency_ms REAL NOT NULL,
  quality REAL,
  success INTEGER,
  task_type TEXT NOT NULL,
  created_at REAL NOT NULL,
  endpoint_fingerprint TEXT NOT NULL,
  source TEXT NOT NULL,
  public_example INTEGER NOT NULL,
  FOREIGN KEY(provider_id) REFERENCES providers(provider_id)
);
CREATE INDEX IF NOT EXISTS idx_obs_provider ON observations(provider_id);
CREATE INDEX IF NOT EXISTS idx_obs_task_type ON observations(task_type);
CREATE INDEX IF NOT EXISTS idx_obs_created ON observations(created_at);
CREATE TABLE IF NOT EXISTS slates(
  slate_id TEXT PRIMARY KEY,
  query_text TEXT NOT NULL,
  item_json TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS choices(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slate_id TEXT NOT NULL,
  blind_id TEXT NOT NULL,
  chosen_observation_id TEXT NOT NULL,
  buyer_id TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS pairwise_preferences(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  query_text TEXT NOT NULL,
  winner_provider TEXT NOT NULL,
  loser_provider TEXT NOT NULL,
  buyer_id TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS outcomes(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  observation_id TEXT NOT NULL,
  buyer_id TEXT NOT NULL,
  success INTEGER NOT NULL,
  score REAL,
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS provider_funds(
  provider_id TEXT PRIMARY KEY,
  balance_usd REAL NOT NULL DEFAULT 0,
  spent_usd REAL NOT NULL DEFAULT 0,
  updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS subsidy_offers(
  offer_id TEXT PRIMARY KEY,
  provider_id TEXT NOT NULL,
  request_text TEXT NOT NULL,
  normal_price_usd REAL NOT NULL,
  subsidy_usd REAL NOT NULL,
  voi REAL NOT NULL,
  reason TEXT NOT NULL,
  expires_at REAL NOT NULL,
  status TEXT NOT NULL DEFAULT 'offered'
);
"""


class Store:
    def __init__(self, path: str | Path = "arena402.sqlite", embedder=None):
        self.path = str(path)
        self.embedder = embedder or HashingEmbedder()
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def add_provider(self, provider: Provider) -> None:
        with self._lock:
            self.conn.execute(
                """INSERT INTO providers VALUES(?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(provider_id) DO UPDATE SET
                   label=excluded.label, endpoint=excluded.endpoint,
                   price_usd=excluded.price_usd, category=excluded.category,
                   endpoint_fingerprint=excluded.endpoint_fingerprint,
                   metadata_json=excluded.metadata_json,
                   capability_family=excluded.capability_family,
                   upstream_family=excluded.upstream_family,
                   pipeline_fingerprint=excluded.pipeline_fingerprint""",
                (
                    provider.provider_id,
                    provider.label,
                    provider.endpoint,
                    provider.price_usd,
                    provider.category,
                    provider.endpoint_fingerprint,
                    json.dumps(provider.metadata, sort_keys=True),
                    provider.capability_family,
                    provider.upstream_family,
                    provider.pipeline_fingerprint,
                ),
            )
            self.conn.commit()

    def providers(self) -> list[dict]:
        return [dict(r) for r in self.conn.execute("SELECT * FROM providers ORDER BY provider_id")]

    def provider(self, provider_id: str) -> dict | None:
        r = self.conn.execute("SELECT * FROM providers WHERE provider_id=?", (provider_id,)).fetchone()
        return dict(r) if r else None

    def add_observation(self, obs: Observation) -> str:
        obs = obs.with_ids()
        vec = self.embedder.embed(obs.request_text)
        with self._lock:
            self.conn.execute(
                """INSERT OR REPLACE INTO observations VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    obs.observation_id,
                    obs.request_id,
                    obs.request_text,
                    json.dumps(vec, separators=(",", ":")),
                    obs.provider_id,
                    obs.response_preview,
                    obs.cost_usd,
                    obs.latency_ms,
                    obs.quality,
                    None if obs.success is None else int(obs.success),
                    obs.task_type,
                    obs.created_at,
                    obs.endpoint_fingerprint,
                    obs.source,
                    int(obs.public_example),
                ),
            )
            self.conn.commit()
        return obs.observation_id

    def add_observations(self, observations: Iterable[Observation]) -> int:
        n = 0
        for obs in observations:
            self.add_observation(obs)
            n += 1
        return n

    def observations(self, *, limit: int | None = None) -> list[dict]:
        q = "SELECT * FROM observations ORDER BY created_at DESC"
        args: tuple = ()
        if limit:
            q += " LIMIT ?"
            args = (limit,)
        return [dict(r) for r in self.conn.execute(q, args)]

    def save_slate(self, slate_id: str, query: str, items: list[dict]) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO slates VALUES(?,?,?,?)",
            (slate_id, query, json.dumps(items, sort_keys=True), time.time()),
        )
        self.conn.commit()

    def get_slate(self, slate_id: str) -> dict | None:
        r = self.conn.execute("SELECT * FROM slates WHERE slate_id=?", (slate_id,)).fetchone()
        if not r:
            return None
        d = dict(r)
        d["items"] = json.loads(d.pop("item_json"))
        return d

    def record_choice(self, slate_id: str, blind_id: str, buyer_id: str = "anonymous", provenance: str = "ORGANIC") -> dict:
        """Record choice with provenance tag per 402molt:834."""
        slate = self.get_slate(slate_id)
        if not slate:
            raise KeyError("unknown slate")
        chosen = next((x for x in slate["items"] if x["blind_id"] == blind_id), None)
        if not chosen:
            raise KeyError("unknown blind id")
        now = time.time()
        # V2: provenance tag ORGANIC/ARENA_COMMISSIONED/PROVIDER_SPONSORED/SELF_REPORTED
        self.conn.execute(
            "INSERT INTO choices(slate_id,blind_id,chosen_observation_id,buyer_id,created_at) VALUES(?,?,?,?,?)",
            (slate_id, blind_id, chosen["observation_id"], buyer_id, now),
        )
        # IMPORTANT: a single reveal choice is not evidence that the selected provider
        # beats every unseen alternative. Pairwise relations are recorded only from a
        # committed partial order / tournament via record_partial_order().
        self.conn.commit()
        return chosen

    def record_partial_order(self, slate_id: str, tiers: list[list[str]], buyer_id: str = "anonymous") -> int:
        """Record only comparisons implied by an explicit consequential partial order.

        `tiers` contains blind IDs, best tier first. Items inside a tier are tied /
        incomparable and generate no pairwise edge.
        """
        slate = self.get_slate(slate_id)
        if not slate:
            raise KeyError("unknown slate")
        by_blind = {x["blind_id"]: x for x in slate["items"]}
        flat = [x for tier in tiers for x in tier]
        if len(flat) != len(set(flat)) or any(x not in by_blind for x in flat):
            raise ValueError("invalid partial order")
        now = time.time(); n = 0
        for i, better in enumerate(tiers):
            for worse in tiers[i+1:]:
                for a in better:
                    for b in worse:
                        pa, pb = by_blind[a]["provider_id"], by_blind[b]["provider_id"]
                        if pa == pb:
                            continue
                        self.conn.execute(
                            "INSERT INTO pairwise_preferences(query_text,winner_provider,loser_provider,buyer_id,created_at) VALUES(?,?,?,?,?)",
                            (slate["query_text"], pa, pb, buyer_id, now),
                        ); n += 1
        self.conn.commit()
        return n

    def record_outcome(self, observation_id: str, success: bool, score: float | None, buyer_id: str) -> None:
        self.conn.execute(
            "INSERT INTO outcomes(observation_id,buyer_id,success,score,created_at) VALUES(?,?,?,?,?)",
            (observation_id, buyer_id, int(success), score, time.time()),
        )
        self.conn.commit()

    def pairwise_counts(self) -> list[dict]:
        q = """SELECT winner_provider, loser_provider, COUNT(*) AS wins
               FROM pairwise_preferences GROUP BY winner_provider, loser_provider"""
        return [dict(r) for r in self.conn.execute(q)]

    def fund_provider(self, provider_id: str, amount_usd: float) -> None:
        now = time.time()
        self.conn.execute(
            """INSERT INTO provider_funds(provider_id,balance_usd,spent_usd,updated_at)
               VALUES(?,?,0,?)
               ON CONFLICT(provider_id) DO UPDATE SET
               balance_usd=balance_usd+excluded.balance_usd, updated_at=excluded.updated_at""",
            (provider_id, amount_usd, now),
        )
        self.conn.commit()

    def provider_fund(self, provider_id: str) -> float:
        r = self.conn.execute("SELECT balance_usd FROM provider_funds WHERE provider_id=?", (provider_id,)).fetchone()
        return float(r[0]) if r else 0.0
