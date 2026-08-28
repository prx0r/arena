from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable

from .mechanism import pairwise_from_partial_order


def commitment(slate_id: str, buyer_id: str, ordered_blind_ids: Iterable[str], nonce: str) -> str:
    payload = {
        "slate_id": slate_id,
        "buyer_id": buyer_id,
        "ordered": list(ordered_blind_ids),
        "nonce": nonce,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(raw.encode()).hexdigest()


@dataclass(frozen=True)
class TournamentResult:
    finalists: tuple[str, ...]
    first_reveal: str
    second_reveal: str | None
    eliminated: tuple[str, ...]

    def partial_order(self) -> tuple[tuple[str, ...], ...]:
        if self.second_reveal and self.second_reveal != self.first_reveal:
            return ((self.first_reveal,), (self.second_reveal,), self.eliminated)
        return ((self.first_reveal,), tuple(x for x in self.finalists if x != self.first_reveal), self.eliminated)

    def pairwise(self) -> list[tuple[str, str, float]]:
        return pairwise_from_partial_order(self.partial_order())


def validate_tournament(all_blind_ids: Iterable[str], finalists: Iterable[str], reveal_order: Iterable[str]) -> TournamentResult:
    all_ids = tuple(dict.fromkeys(all_blind_ids))
    fin = tuple(dict.fromkeys(finalists))
    rev = tuple(dict.fromkeys(reveal_order))
    if not all_ids:
        raise ValueError("empty slate")
    if not (1 <= len(fin) <= min(2, len(all_ids))):
        raise ValueError("keep one or two finalists")
    if any(x not in all_ids for x in fin):
        raise ValueError("unknown finalist")
    if not rev or rev[0] not in fin:
        raise ValueError("first reveal must be a finalist")
    if len(rev) > 2 or any(x not in fin for x in rev):
        raise ValueError("only finalists can be revealed")
    eliminated = tuple(x for x in all_ids if x not in fin)
    return TournamentResult(fin, rev[0], rev[1] if len(rev) > 1 else None, eliminated)
