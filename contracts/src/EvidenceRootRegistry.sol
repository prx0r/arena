// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title 402Arena EvidenceRootRegistry
/// @notice Cheap temporal anchoring for off-chain evidence batches. Raw requests,
///         outputs and personal data remain off-chain; only batch commitments land here.
contract EvidenceRootRegistry {
    address public immutable operator;

    struct Batch {
        bytes32 root;
        uint64 count;
        uint64 timestamp;
        bytes32 previousRoot;
    }

    mapping(bytes32 => Batch) public batches;
    bytes32 public latestRoot;

    event EvidenceBatchAnchored(bytes32 indexed batchId, bytes32 indexed root, uint256 count, bytes32 previousRoot);

    error Unauthorized();
    error ExistingBatch();
    error InvalidBatch();

    constructor(address operator_) {
        if (operator_ == address(0)) revert Unauthorized();
        operator = operator_;
    }

    function anchor(bytes32 batchId, bytes32 root, uint64 count) external {
        if (msg.sender != operator) revert Unauthorized();
        if (batchId == bytes32(0) || root == bytes32(0) || count == 0) revert InvalidBatch();
        if (batches[batchId].timestamp != 0) revert ExistingBatch();
        bytes32 prev = latestRoot;
        batches[batchId] = Batch(root, count, uint64(block.timestamp), prev);
        latestRoot = root;
        emit EvidenceBatchAnchored(batchId, root, count, prev);
    }
}
