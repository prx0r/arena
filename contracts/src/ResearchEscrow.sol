// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IERC20Minimal {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/// @title 402Arena ResearchEscrow
/// @notice Provider-funded research budget. Money can buy measured experiments,
///         never organic rank. The Arena operator can only spend a campaign's
///         deposited token balance on auditable bounty events.
contract ResearchEscrow {
    IERC20Minimal public immutable token;
    address public immutable operator;

    struct Campaign {
        address owner;
        uint128 balance;
        uint128 funded;
        bool closed;
    }

    mapping(bytes32 => Campaign) public campaigns;
    mapping(bytes32 => bool) public bountyPaid;
    bool private locked;

    event CampaignFunded(bytes32 indexed campaignId, address indexed owner, uint256 amount, uint256 newBalance);
    event BountyPaid(bytes32 indexed campaignId, bytes32 indexed bountyId, address indexed agent, uint256 amount, bytes32 evidenceHash);
    event CampaignClosed(bytes32 indexed campaignId, address indexed owner);
    event CampaignRefunded(bytes32 indexed campaignId, address indexed owner, uint256 amount);

    error Unauthorized();
    error InvalidAmount();
    error Closed();
    error InsufficientBalance();
    error Replay();
    error TransferFailed();
    error Reentrancy();

    modifier nonReentrant() {
        if (locked) revert Reentrancy();
        locked = true;
        _;
        locked = false;
    }

    constructor(address token_, address operator_) {
        if (token_ == address(0) || operator_ == address(0)) revert Unauthorized();
        token = IERC20Minimal(token_);
        operator = operator_;
    }

    function fundCampaign(bytes32 campaignId, uint256 amount) external nonReentrant {
        if (amount == 0 || amount > type(uint128).max) revert InvalidAmount();
        Campaign storage c = campaigns[campaignId];
        if (c.owner == address(0)) c.owner = msg.sender;
        if (c.owner != msg.sender) revert Unauthorized();
        if (c.closed) revert Closed();
        if (!token.transferFrom(msg.sender, address(this), amount)) revert TransferFailed();
        c.balance += uint128(amount);
        c.funded += uint128(amount);
        emit CampaignFunded(campaignId, msg.sender, amount, c.balance);
    }

    function payBounty(bytes32 campaignId, bytes32 bountyId, address agent, uint256 amount, bytes32 evidenceHash)
        external nonReentrant
    {
        if (msg.sender != operator) revert Unauthorized();
        if (agent == address(0) || amount == 0 || amount > type(uint128).max) revert InvalidAmount();
        if (bountyPaid[bountyId]) revert Replay();
        Campaign storage c = campaigns[campaignId];
        if (c.closed) revert Closed();
        if (c.balance < amount) revert InsufficientBalance();
        bountyPaid[bountyId] = true;
        c.balance -= uint128(amount);
        if (!token.transfer(agent, amount)) revert TransferFailed();
        emit BountyPaid(campaignId, bountyId, agent, amount, evidenceHash);
    }

    function closeCampaign(bytes32 campaignId) external {
        Campaign storage c = campaigns[campaignId];
        if (c.owner != msg.sender) revert Unauthorized();
        c.closed = true;
        emit CampaignClosed(campaignId, msg.sender);
    }

    function refund(bytes32 campaignId, uint256 amount) external nonReentrant {
        Campaign storage c = campaigns[campaignId];
        if (c.owner != msg.sender) revert Unauthorized();
        if (!c.closed) revert Closed();
        if (amount == 0 || c.balance < amount) revert InsufficientBalance();
        c.balance -= uint128(amount);
        if (!token.transfer(msg.sender, amount)) revert TransferFailed();
        emit CampaignRefunded(campaignId, msg.sender, amount);
    }
}
