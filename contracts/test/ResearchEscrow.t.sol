// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import "../src/ResearchEscrow.sol";
import "../src/MockUSDC.sol";

interface Vm { function prank(address) external; }

contract ResearchEscrowTest {
    Vm constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    MockUSDC usdc;
    ResearchEscrow escrow;
    address provider = address(0xBEEF);
    address agent = address(0xA11CE);
    bytes32 campaign = keccak256("campaign");

    constructor() {
        usdc = new MockUSDC();
        escrow = new ResearchEscrow(address(usdc), address(this));
        usdc.mint(provider, 100_000_000);
    }

    function testFundAndPay() public {
        vm.prank(provider); usdc.approve(address(escrow), 10_000_000);
        vm.prank(provider); escrow.fundCampaign(campaign, 10_000_000);
        escrow.payBounty(campaign, keccak256("b1"), agent, 2_000_000, keccak256("evidence"));
        require(usdc.balanceOf(agent)==2_000_000,"agent paid");
        (,uint128 bal,,)=escrow.campaigns(campaign);
        require(bal==8_000_000,"balance");
    }
}
