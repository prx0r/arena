from __future__ import annotations

from dataclasses import dataclass
import json
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class BaseNetwork:
    name: str
    chain_id: int
    caip2: str
    rpc_url: str
    usdc_address: str
    explorer: str
    is_testnet: bool


BASE_SEPOLIA = BaseNetwork(
    name="Base Sepolia",
    chain_id=84532,
    caip2="eip155:84532",
    rpc_url="https://sepolia.base.org",
    usdc_address="0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    explorer="https://sepolia.basescan.org",
    is_testnet=True,
)

BASE_MAINNET = BaseNetwork(
    name="Base",
    chain_id=8453,
    caip2="eip155:8453",
    rpc_url="https://mainnet.base.org",
    usdc_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    explorer="https://basescan.org",
    is_testnet=False,
)


def rpc_chain_id(network: BaseNetwork = BASE_SEPOLIA, timeout: float = 5.0) -> int:
    """Optional smoke check. No private key and no transaction required."""
    body = json.dumps({"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}).encode()
    req = Request(network.rpc_url, data=body, headers={"content-type":"application/json"})
    with urlopen(req, timeout=timeout) as response:
        data = json.loads(response.read())
    return int(data["result"], 16)


def assert_network(network: BaseNetwork = BASE_SEPOLIA, timeout: float = 5.0) -> None:
    got = rpc_chain_id(network, timeout)
    if got != network.chain_id:
        raise RuntimeError(f"RPC chain mismatch: expected {network.chain_id}, got {got}")
