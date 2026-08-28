from __future__ import annotations
from hashlib import sha256


def h(data: bytes) -> bytes:
    return sha256(data).digest()


def leaf(payload: bytes) -> bytes:
    return h(b"\x00" + payload)


def parent(a: bytes, b: bytes) -> bytes:
    return h(b"\x01" + a + b)


def merkle_root(payloads: list[bytes]) -> str:
    if not payloads:
        return "0x" + h(b"").hex()
    layer = [leaf(x) for x in payloads]
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [parent(layer[i], layer[i + 1]) for i in range(0, len(layer), 2)]
    return "0x" + layer[0].hex()
