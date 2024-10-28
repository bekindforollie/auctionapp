from app.classes.models.bids import Bids_Methods
from app.classes.helpers.config_helpers import Config_Helpers
from app.classes.models.auction_items import AuctionItems_Methods
from app.classes.models.item_donors import ItemDonors_Methods

class Auction_Items_Helpers:
    @staticmethod
    def get_starting_bid(
        item_id: int
    ):
        if Config_Helpers.is_min_bid_percent():
            item = AuctionItems_Methods.get_item_by_id(item_id)
            price = item.item_price * (Config_Helpers.get_min_bid_amount()/100)
            return price
        else:
            return Config_Helpers.get_min_bid_amount()

    @staticmethod
    def get_highest_bid(
        item_id: int
    ):
        bids = Bids_Methods.get_bids_by_item_id(item_id)
        sorted_bids = sorted(bids, key=lambda x: x["bid_amount"], reverse=True)
        return sorted_bids[0]

    @staticmethod
    def get_current_bid(
        item_id: int
    ):
        starting_bid = Auction_Items_Helpers.get_starting_bid(item_id)
        try:
            bids = Bids_Methods.get_bid_by_id(item_id)
            sorted_bids = sorted(bids, key=lambda x: x["bid_amount"], reverse=True)
            if sorted_bids[0]["bid_amount"] > starting_bid:
                return sorted_bids[0]["bid_amount"]
            else:
                return starting_bid
        except Exception as e:
            print(f"Database error: {e}")
            return starting_bid
        
    @staticmethod    
    def get_donor_name(
        donor_id: int
    ):
        donor = ItemDonors_Methods.get_donor_by_id(donor_id)
        
        if donor.company_name is not None:
            donor_name = donor.company_name
        else:
            donor_name = f"{donor.donor_firstname} {donor.donor_lastname}"

        return donor_name
    @staticmethod
    def get_item_details(
        item_id: int
    ):
        item_out = {}
        item = AuctionItems_Methods.get_item_by_id(item_id)
        item_out["item_id"] = item["item_id"]
        item_out["starting_bid"] = Auction_Items_Helpers.get_starting_bid(item.item_id)
        item_out["highest_bid"] = Auction_Items_Helpers.get_current_bid(item.item_id)
        item_out["donor_name"] = Auction_Items_Helpers.get_donor_name(item["donor_id"])
        item_out["item_image"] = item["item_image"]
        item_out["item_title"] = item["item_title"]
        return item_out