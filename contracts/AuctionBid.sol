// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AuctionBid {
    struct Item {
        string bidder;
        string owner;
        string item;
        string itemId;
        uint256 amount;
        uint256 timestamp;
    }

    // Array to store all items
    Item[] public items;
    
    function addItem(
        string memory _bidder,
        string memory _owner,
        string memory _item,
        string memory _itemId,
        uint256 _amount
    ) public {
        require(bytes(_bidder).length > 0, "Bidder cannot be empty");
        require(bytes(_owner).length > 0, "Owner cannot be empty");
        require(bytes(_item).length > 0, "Item cannot be empty");
        require(bytes(_itemId).length > 0, "ItemId cannot be empty");
        require(_amount > 0, "Amount must be greater than 0");

        Item memory newItem = Item({
            bidder: _bidder,
            owner: _owner,
            item: _item,
            itemId: _itemId,
            amount: _amount,
            timestamp: block.timestamp
        });

        items.push(newItem);
    }

    function getItemCount() public view returns (uint256) {
        return items.length;
    }

    function getItem(uint256 index) public view returns (
        string memory bidder,
        string memory owner,
        string memory item,
        string memory itemId,
        uint256 amount,
        uint256 timestamp
    ) {
        require(index < items.length, "Index out of bounds");
        Item memory _item = items[index];
        return (
            _item.bidder,
            _item.owner,
            _item.item,
            _item.itemId,
            _item.amount,
            _item.timestamp
        );
    }

    function getItemsByBidder(string memory _bidder) public view returns (uint256[] memory) {
        uint256[] memory bidderItems = new uint256[](items.length);
        uint256 count = 0;
        
        for(uint256 i = 0; i < items.length; i++) {
            if(keccak256(bytes(items[i].bidder)) == keccak256(bytes(_bidder))) {
                bidderItems[count] = i;
                count++;
            }
        }
        
        // Create a new array with the exact size
        uint256[] memory result = new uint256[](count);
        for(uint256 i = 0; i < count; i++) {
            result[i] = bidderItems[i];
        }
        
        return result;
    }
}
