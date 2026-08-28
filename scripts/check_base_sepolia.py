from arena402.sepolia import BASE_SEPOLIA, assert_network
print(f"Checking {BASE_SEPOLIA.name} ({BASE_SEPOLIA.chain_id}) via {BASE_SEPOLIA.rpc_url}")
assert_network(BASE_SEPOLIA)
print("ok")
