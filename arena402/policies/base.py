from __future__ import annotations
from typing import Protocol


class Policy(Protocol):
    name: str
    def choose(self, context: dict, providers: list[str]) -> str: ...
    def update(self, context: dict, provider: str, quality: float, cost: float, failed: bool) -> None: ...
