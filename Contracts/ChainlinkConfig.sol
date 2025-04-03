// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import {ConfirmedOwner} from "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";

contract ChainlinkConfig is ConfirmedOwner {
    address public chainlinkToken;
    address public chainlinkOracle;
    string public apiEndpoint;
    bytes32 public jobId;
    uint256 public fee;

    constructor(
        address _chainlinkToken,
        address _chainlinkOracle,
        string memory _apiEndpoint,
        bytes32 _jobId,
        uint256 _fee
    ) ConfirmedOwner(msg.sender) {
        chainlinkToken = _chainlinkToken;
        chainlinkOracle = _chainlinkOracle;
        apiEndpoint = _apiEndpoint;
        jobId = _jobId;
        fee = _fee;
    }

    function updateConfig(
        address _chainlinkToken,
        address _chainlinkOracle,
        string memory _apiEndpoint,
        bytes32 _jobId,
        uint256 _fee
    ) public onlyOwner {
        chainlinkToken = _chainlinkToken;
        chainlinkOracle = _chainlinkOracle;
        apiEndpoint = _apiEndpoint;
        jobId = _jobId;
        fee = _fee;
    }
} 