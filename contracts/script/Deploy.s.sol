// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../src/ResearchEscrow.sol";
import "../src/EvidenceRootRegistry.sol";

interface Vm { function envAddress(string calldata) external returns (address); function startBroadcast() external; function stopBroadcast() external; }

contract Deploy {
    Vm constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    function run() external returns (ResearchEscrow escrow, EvidenceRootRegistry registry) {
        address usdc = vm.envAddress("USDC_ADDRESS");
        address operator = vm.envAddress("ARENA_OPERATOR");
        vm.startBroadcast();
        escrow = new ResearchEscrow(usdc, operator);
        registry = new EvidenceRootRegistry(operator);
        vm.stopBroadcast();
    }
}
