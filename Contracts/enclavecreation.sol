// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import {Chainlink, ChainlinkClient} from "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import {ConfirmedOwner} from "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";
import {LinkTokenInterface} from "@chainlink/contracts/src/v0.8/shared/interfaces/LinkTokenInterface.sol";

contract FastAPIPinger is ChainlinkClient, ConfirmedOwner {
    using Chainlink for Chainlink.Request;

    string public apiResponse;
    bytes32 private jobId;
    uint256 private fee;

    event APIResponseReceived(bytes32 indexed requestId, string apiResponse);

    constructor() ConfirmedOwner(msg.sender) {
        _setChainlinkToken(0x779877A7B0D9E8603169DdbD7836e478b4624789);
        _setChainlinkOracle(0x6090149792dAAeE9D1D568c9f9a6F6B46AA29eFD);
        jobId = "ca98366cc7314957b8c012c72f05aeeb";
        fee = (1 * LINK_DIVISIBILITY) / 10; // 0.1 LINK
    }

    struct enclave_details

    {
      
      string enclaveid;
      string enclave_endpoint;
      string pcr0;
      string pcr1;
      string pcr2;
      string pcr8;
    
    }

    mapping(string => enclave_details) public available_enclaves;
    string[] public enclaveids;

    function requestFastAPIData() public returns (bytes32 requestId) {
        Chainlink.Request memory req = _buildChainlinkRequest(
            jobId,
            address(this),
            this.fulfill.selector 
        );

        req._add("get", "https://7953-103-214-61-117.ngrok-free.app/api/test");

        req._add("path", "data.enclaveid");
        req._add("path","data.pcr0");
        req._add("path","data.pcr1");
        req._add("path","data.pcr2");
        req._add("path","data.pcr8");
        req._add("path","data.enclave_endpoint");

        return _sendChainlinkRequest(req, fee);
    }

    function addingenclaves(string memory enclaveid, string memory pcr0, string memory pcr1, string memory pcr2, string memory pcr8, string memory enclave_endpoint) private 
    {
        enclave_details memory newEnclave = enclave_details({
            enclaveid: enclaveid,
            enclave_endpoint: enclave_endpoint,
            pcr0: pcr0,
            pcr1: pcr1,
            pcr2: pcr2,
            pcr8: pcr8
        });

        available_enclaves[enclaveid] = newEnclave;
        enclaveids.push(enclaveid);
    }

    function fulfill(
        bytes32 _requestId,
        string memory enclaveid,
        string memory enclave_endpoint,
        string memory pcr0,
        string memory pcr1,
        string memory pcr2,
        string memory pcr8
    ) public recordChainlinkFulfillment(_requestId)
     {
        addingenclaves(enclaveid, pcr0, pcr1, pcr2, pcr8, enclave_endpoint);
        emit APIResponseReceived(_requestId, enclaveid);
    }
 
    function viewenclaves(string memory enclaveid) public view  returns (enclave_details memory) 
    {

       return available_enclaves[enclaveid];

    }

    function withdrawLink() public onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(_chainlinkTokenAddress());
        require(
            link.transfer(msg.sender, link.balanceOf(address(this))),
            "Unable to transfer"
        );
    }
}
