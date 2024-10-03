from peewee import(
    AutoField,
    CharField,
    ForeignKeyField,
    DateTimeField,
    DecimalField
)
import datetime

# Models import
from app.classes.models.base_model import BaseModel
from app.classes.models.users import Users
from app.classes.models.auction_items import AuctionItems


# Helpers import
from app.classes.helpers.db_helpers import DatabaseHelpers
from app.classes.helpers.shared_helpers import Helpers


# Bids Model
class Bids (BaseModel):
    bid_id= AutoField(primary_key = True, unique=True)
    bid_amount= DecimalField(default =0)
    bid_time = DateTimeField
    item_id = ForeignKeyField(AuctionItems, to_field="item_id")
    user_id = ForeignKeyField(Users, to_field= "user_id")

    class Meta:
        table_name="Bids"

    #Bids Class/Methods
class Bids_Methods:
    def __init__(self, database):
        self.database = database

    @staticmethod
    def create_bid(
        bid_amount: float,
        bid_time: datetime, 
        item_id: int,
        user_id: int
    ) -> int:
        """
        Creates a bid in the database

        Args:
            bid_amount: The dollar amount the user bids
            bid_time: The date and time of the bid
            item_id: The auction item ID; foreign key to Auction_Items table
            user_id: The user ID; foreign key to Users table
           
        Returns:
            int: The numeric ID of the new bid ####Is this right??

        Raises:
            PeeweeException: If the bid ID already exists or if user_id or item_id failed foreign key validation
        
        """
        return Bids.create(
            bid_amount=bid_amount,
            bid_time=bid_time,
          
        ).bid_id
    
    @staticmethod
    def get_all_bids():
        query = Bids.select()
        return DatabaseHelpers.get_rows(query)
    
    @staticmethod
    def get_item_by_bid(bid_id: int):
        return Bids.select().where(Bids.bid_id == bid_id)
    
    @staticmethod
    def update_bid(bid_obj: object):
        return bid_obj.save()
    
    def remove_bid(self, bid_id):
        Bids.delete().where(Bids.bid_id == bid_id).execute()
        return True