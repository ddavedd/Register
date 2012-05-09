"""A file with the format of the tables we are using in the database"""
import datetime
import timeformat

class Deal:
    """A special for a multiple number of products"""
    def __init__(self, db_row):
        deal_id, product_id, product_count, enabled = range(4)
        self.id = db_row[deal_id]
        self.product_id = db_row[product_id]
        self.product_count = db_row[product_count]
        self.enabled = bool(db_row[enabled])

class DealPrice:
    """The price for a deal on products"""
    def __init__(self, db_row):
        deal_price_id, deal_price, deal_timestamp = range(3) 
        self.id = db_row[deal_price_id]
        self.price = db_row[deal_price]
        self.timestamp = db_row[deal_timestamp]
        

class ProductPrice:
    """The price of a product"""
    def __init__(self, db_row):
        product_price_id, price, timestamp = range(3)
        self.id = db_row[product_price_id]
        self.price = db_row[price]
        self.timestamp = datetime.datetime.strptime(db_row[timestamp], timeformat.get_time_format_string())

        
class Item:
    """A basic item from the database"""
    def __init__(self, db_row):
        item_id, item_name = range(2)
        self.id = db_row[item_id]
        self.name = db_row[item_name]

       
class Product:
    """A product with a price, tax_rate, etc."""
    def __init__(self, db_row):
        product_id, name, is_by_weight, item, item_count, tax_rate, enabled, is_premarked = range(8)
        self.id = db_row[product_id]
        self.name = db_row[name]
        self.is_by_weight = bool(db_row[is_by_weight])
        self.item = db_row[item]
        self.item_count = db_row[item_count]
        self.is_nonedible = bool(db_row[tax_rate])
        self.enabled = bool(db_row[enabled])
        self.is_premarked = bool(db_row[is_premarked])
        
    def get_item_ending(self):
        """Get the way to refer to an entry, either each or per pound"""
        if self.is_by_weight:
            return "per pound"
        else:
            return "each"


class Category:
    """A category that products are lumped in to"""
    def __init__(self, db_row):
        category_id, category_name = range(2)
        self.id = db_row[category_id]
        self.name = db_row[category_name]
