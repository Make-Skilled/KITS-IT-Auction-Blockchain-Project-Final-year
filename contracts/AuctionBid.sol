// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AuctionBid {
    struct Bid {
        address bidder;
        uint256 amount;
        uint256 timestamp;
    }
    
    mapping(uint256 => Bid[]) public auctionBids; // Maps auction ID to list of bids
    
    event NewBid(uint256 indexed auctionID, address indexed bidder, uint256 amount, uint256 timestamp);
    
    function placeBid(uint256 _auctionID) external payable {
        require(msg.value > 0, "Bid amount must be greater than zero");
        
        auctionBids[_auctionID].push(Bid({
            bidder: msg.sender,
            amount: msg.value,
            timestamp: block.timestamp
        }));
        
        emit NewBid(_auctionID, msg.sender, msg.value, block.timestamp);
    }
    
    function getBids(uint256 _auctionID) external view returns (Bid[] memory) {
        return auctionBids[_auctionID];
    }
}