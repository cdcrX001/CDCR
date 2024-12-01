// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import {Chainlink, ChainlinkClient} from "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import {ConfirmedOwner} from "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";
import {LinkTokenInterface} from "@chainlink/contracts/src/v0.8/shared/interfaces/LinkTokenInterface.sol";

contract EnclaveManager is ChainlinkClient, ConfirmedOwner {
    using Chainlink for Chainlink.Request;

    struct EnclaveData {
        address user;
        string encryptedDetails;
        uint256 createdAt;
    }

    mapping(bytes32 => EnclaveData) public enclaveRequests;
    mapping(address => bytes32[]) public userRequests;

    bytes32 private jobId;
    uint256 private fee;
    uint256 public constant MAX_USER_REQUESTS = 20;
    uint256 public constant REQUEST_EXPIRY = 1 hours;

    event EnclaveRequested(bytes32 indexed requestId, address indexed user);
    event EnclaveFulfilled(bytes32 indexed requestId, string encryptedDetails);

     constructor() ConfirmedOwner(msg.sender) {
        _setChainlinkToken(0x779877A7B0D9E8603169DdbD7836e478b4624789);
        _setChainlinkOracle(0x6090149792dAAeE9D1D568c9f9a6F6B46AA29eFD);
        jobId = "7d80a6386ef543a3abb52817f6707e3b";
        fee = (1 * LINK_DIVISIBILITY) / 10; // 0,1 * 10**18 (Varies by network and job)
    }

    function requestEnclaveCreation(string memory publicKey) 
        public 
        payable 
        returns (bytes32 requestId) 
    {
        // Validate input
        require(bytes(publicKey).length > 0, "Invalid public key");
        require(userRequests[msg.sender].length < MAX_USER_REQUESTS, "Exceeded max requests");

        Chainlink.Request memory req = _buildChainlinkRequest(
            jobId,
            address(this),
            this.fulfill.selector
        );
          string memory url = string(abi.encodePacked(
        "https://cb9d7767-726f-4228-be77-c0b623123183-00-1si2vx8eba5ey.sisko.replit.dev/api/test?publicKey=",
        publicKey
    ));

        req._add("get", url);
        req._add("path","0,data");

        requestId = _sendChainlinkRequest(req, fee);
        
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
        jobId = _jobId;
        fee = _fee;
    }
}