// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import {Chainlink, ChainlinkClient} from "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import {ConfirmedOwner} from "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";
import {LinkTokenInterface} from "@chainlink/contracts/src/v0.8/shared/interfaces/LinkTokenInterface.sol";
import "./ChainlinkConfig.sol";

contract FetchFromArray is ChainlinkClient, ConfirmedOwner {
    using Chainlink for Chainlink.Request;

    string public data;
    ChainlinkConfig public config;

    event RequestFirstId(bytes32 indexed requestId, string data);

    constructor(address _configAddress) ConfirmedOwner(msg.sender) {
        config = ChainlinkConfig(_configAddress);
        _setChainlinkToken(config.chainlinkToken());
        _setChainlinkOracle(config.chainlinkOracle());
    }

    function requestFirstId() public returns (bytes32 requestId) {
        Chainlink.Request memory req = _buildChainlinkRequest(
            config.jobId(),
            address(this),
            this.fulfill.selector
        );

        req._add("get", config.apiEndpoint());
        req._add("path", "0,data");
        
        return _sendChainlinkRequest(req, config.fee());
    }

    /**
     * Receive the response in the form of string
     */
    function fulfill(
        bytes32 _requestId,
        string memory _data
    ) public recordChainlinkFulfillment(_requestId) {
        emit RequestFirstId(_requestId, _data);
        data = _data;
    }

    /**
     * Allow withdraw of Link tokens from the contract
     */
    function withdrawLink() public onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(_chainlinkTokenAddress());
        require(
            link.transfer(msg.sender, link.balanceOf(address(this))),
            "Unable to transfer"
        );
    }
}
