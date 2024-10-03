from peewee import (
    AutoField,
    ForeignKeyField
)

# Models import
from app.classes.models.base_model import BaseModel
from app.classes.models.main_cart import MainCart
from app.classes.models.merchandise_items import MerchandiseItems

# Helpers import
from app.classes.helpers.db_helpers import DatabaseHelpers

# Auction Items Model
class CartMerchItems(BaseModel):
    entry_id = AutoField(primary_key=True, unique=True)
    cart_id = ForeignKeyField(MainCart, to_field="cart_id")
    merch_id = ForeignKeyField(MerchandiseItems, to_field="merch_id")
    class Meta:
        table_name = "CartMerchItems"

# CartMerchItems Class/Methods
class CartMerchItems_Methods:
    def __init__(self, database):
        self.database = database

    @staticmethod
    def create_cart(
        cart_id: int,
        merch_id: int
    ) -> int:
        """
        Creates an auction item in the database

        Args:
            item_title: The name/title of the merch item
            item_description: A brief description of the item
            item_price: The price (in dollars) of the item
            item_image: The path to the item image
        
        Returns:
            int: The numeric ID of the new item

        Raises:
            PeeweeException: If the item ID already exists
        """
        return CartMerchItems.create(
            cart_id=cart_id,
            merch_id=merch_id,
        ).entry_id
    
    @staticmethod
    def get_all_carts():
        query = CartMerchItems.select()
        return DatabaseHelpers.get_rows(query)
    
    @staticmethod
    def get_cart_by_id(entry_id: int):
        return CartMerchItems.select().where(CartMerchItems.entry_id == entry_id)
    
    @staticmethod
    def update_cart(item_obj: object):
        return item_obj.save()
    
    def remove_cart(self, entry_id):
        CartMerchItems.delete().where(CartMerchItems.entry_id == entry_id).execute()
        return True