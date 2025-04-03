// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import {Chainlink, ChainlinkClient} from "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import {ConfirmedOwner} from "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";
import {LinkTokenInterface} from "@chainlink/contracts/src/v0.8/shared/interfaces/LinkTokenInterface.sol";
import "./ChainlinkConfig.sol";

contract EnclaveManager is ChainlinkClient, ConfirmedOwner {
    using Chainlink for Chainlink.Request;

    struct EnclaveData {
        address user;
        string encryptedDetails;
        uint256 createdAt;
    }

    mapping(bytes32 => EnclaveData) public enclaveRequests;
    mapping(address => bytes32[]) public userRequests;

    ChainlinkConfig public config;
    uint256 public constant MAX_USER_REQUESTS = 20;
    uint256 public constant REQUEST_EXPIRY = 1 hours;

    event EnclaveRequested(bytes32 indexed requestId, address indexed user);
    event EnclaveFulfilled(bytes32 indexed requestId, string encryptedDetails);

    constructor(address _configAddress) ConfirmedOwner(msg.sender) {
        config = ChainlinkConfig(_configAddress);
        _setChainlinkToken(config.chainlinkToken());
        _setChainlinkOracle(config.chainlinkOracle());
    }

    function requestEnclaveCreation(string memory publicKey) 
        public 
        payable 
        returns (bytes32 requestId) 
    {
        require(bytes(publicKey).length > 0, "Invalid public key");
        require(userRequests[msg.sender].length < MAX_USER_REQUESTS, "Exceeded max requests");

        Chainlink.Request memory req = _buildChainlinkRequest(
            config.jobId(),
            address(this),
            this.fulfill.selector
        );

        string memory url = string(abi.encodePacked(
            config.apiEndpoint(),
            "?publicKey=",
            publicKey
        ));

        req._add("get", url);
        req._add("path","0,data");

        requestId = _sendChainlinkRequest(req, config.fee());
        
        enclaveRequests[requestId] = EnclaveData({
            user: msg.sender,
            encryptedDetails: "",
            createdAt: block.timestamp
        });
        
        userRequests[msg.sender].push(requestId);
        emit EnclaveRequested(requestId, msg.sender);
        return requestId;
    }

    function fulfill(
        bytes32 _requestId,
        string memory encryptedDetails
    ) public recordChainlinkFulfillment(_requestId) {
        EnclaveData storage enclaveData = enclaveRequests[_requestId];
        
        require(enclaveData.user != address(0), "Invalid request ID");
        require(block.timestamp - enclaveData.createdAt <= REQUEST_EXPIRY, "Request expired");

        enclaveData.encryptedDetails = encryptedDetails;
        emit EnclaveFulfilled(_requestId, encryptedDetails);
    }

    function getEnclaveDetails(bytes32 requestId) 
        public 
        view 
        returns (string memory) 
    {
        EnclaveData memory enclaveData = enclaveRequests[requestId];
        require(enclaveData.user == msg.sender, "Unauthorized access");
        require(bytes(enclaveData.encryptedDetails).length > 0, "Enclave details not available");
        return enclaveData.encryptedDetails;
    }

    function withdrawLink() public onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(_chainlinkTokenAddress());
        uint256 balance = link.balanceOf(address(this));
        require(link.transfer(msg.sender, balance), "Unable to transfer");
    }

    function withdrawFunds() public onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");
        payable(msg.sender).transfer(balance);
    }

    // Allow updating Chainlink configuration (only by owner)
    function updateChainlinkConfig(
        address _linkToken, 
        address _oracle, 
        bytes32 _jobId,
        uint256 _fee
    ) public onlyOwner {
        _setChainlinkToken(_linkToken);
        _setChainlinkOracle(_oracle);
        config.updateJobId(_jobId);
        config.updateFee(_fee);
    }
}