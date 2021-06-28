"""A file with the format of the tables we are using in the database"""
import datetime
import timeformat

class Deal:
    """A special for a multiple number of products"""
    def __init__(self, db_row):
        deal_id, product_id, product_count, deal_price, timestamp, enabled = list(range(6))
        self.id = db_row[deal_id]
        self.product_id = db_row[product_id]
        self.product_count = db_row[product_count]
        self.deal_price = db_row[deal_price]
        self.timestamp = db_row[timestamp]
        self.enabled = bool(db_row[enabled])

    def __eq__(self, other):
        #print "Checking if two deals equal"
        return isinstance(other, Deal) and self.__dict__ == other.__dict__

#class DealPrice:
#    """The price for a deal on products"""
#    def __init__(self, db_row):
#       deal_price_id, deal_price, deal_timestamp = range(3) 
#        self.id = db_row[deal_price_id]
#        self.price = db_row[deal_price]
#        self.timestamp = db_row[deal_timestamp]
#
#    def __eq__(self, other):
#        #print "Checking if two deal prices equal"
#        return isinstance(other, DealPrice) and self.__dict__ == other.__dict__

class ProductPrice:
    """The price of a product"""
    def __init__(self, db_row):
        product_price_id, product_id, price, timestamp = list(range(4))
        self.id = db_row[product_id]
        self.price = db_row[price]
        self.timestamp = db_row[timestamp]

    def __eq__(self, other):
        #print "Checking if two product prices equal"
        return isinstance(other, ProductPrice) and self.__dict__ == other.__dict__
        
class Item:
    """A basic item from the database"""
    def __init__(self, db_row):
        item_id, item_name = list(range(2))
        self.id = db_row[item_id]
        self.name = db_row[item_name]

    def __eq__(self, other):
        #print "Checking if two items equal"
        return isinstance(other, Item) and self.__dict__ == other.__dict__
       
class Product:
    """A product with a price, tax_rate, etc."""
    def __init__(self, db_row):
        product_id, item_id, item_count, name, tax_rate, enabled, product_type, product_color = list(range(8))
        self.id = db_row[product_id]
        self.item = db_row[item_id]
        self.item_count = db_row[item_count]
        self.name = db_row[name]
        self.is_nonedible = bool(db_row[tax_rate])
        self.enabled = bool(db_row[enabled])
        product_type = str(db_row[product_type])
        self.is_by_weight = bool(product_type=="WT")
        self.is_premarked = bool(product_type=="PM")
        self.color = str(db_row[product_color])
        
    def get_item_ending(self):
        """Get the way to refer to an entry, either each or per pound"""
        if self.is_by_weight:
            return "per pound"
        else:
            return "each"
        
    def __eq__(self, other):
        #print "Checking if two products equal"
        return isinstance(other, Product) and self.__dict__ == other.__dict__

class Category:
    """A category that products are lumped in to"""
    def __init__(self, db_row):
        category_id, category_name, category_color, enabled = list(range(4))
        self.id = db_row[category_id]
        self.name = db_row[category_name]
        self.color = str(db_row[category_color])
        self.enabled = bool(db_row[enabled])
        
    def __eq__(self, other):
        #print "Checking if two categories equal"
        return isinstance(other, Category) and self.__dict__ == other.__dict__

