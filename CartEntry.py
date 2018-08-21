"""A collection of classes for entries into the shopping cart"""
class CartEntry:
    """An entry into the register cart"""
    def __init__(self, price_per, amount):
        """Set the initial values of the entry"""    
        self.price_per = price_per
        self.amount = amount
    
    def get_description(self):
        """Get the description of the cart entry"""
        return "Cart Entry set to %f at $%.2f" % (self.amount, self.price_per)
    
    def get_transaction_item_id(self):
        """Get the transaction item id"""
        return None
    
    def is_product(self):
        """Overloaded, return true if this is a product"""
        return -1
    
    def get_amount(self):
        """Get the amount of products in this entry"""
        return self.amount
        
    def price(self):
        """Get the total price of this entry"""
        return float(self.price_per) * float(self.amount)
    
    def change_amount(self, new_amount):
        """Change the amount of products in this entry to a new amount"""
        self.amount = new_amount

    def add_some(self, more):
        """Add more product to this cart entry"""
        self.amount += more

    #def __del__(self):
    #    """Called when this is deleted and cleaned up"""
    #    #print "Deleting a cart entry"

class ProductCartEntry(CartEntry):
    """An entry of a product into the cart"""
    def __init__(self, product, price_per, amount):
        """Initialize the entry with a price and an amount"""
        CartEntry.__init__(self, price_per, amount)
        self.product = product

    def is_product(self):
        """Return true since this is a product"""
        return 1

    def get_transaction_item_id(self):
        """Return the transaction item id of the product"""
        return self.product.id

    def get_description(self):
        """Get the description of the cart entry"""
        # Remove the extra whitespace
        #print self.product.name
        return ' '.join(self.product.name.split())
    
class DealCartEntry(CartEntry):
    """An entry of a deal into the cart"""
    def __init__(self, product, deal, price_per, amount):
        """Initialize the entry with a deal price and number of deals"""
        CartEntry.__init__(self, price_per, amount)
        self.product = product
        self.deal = deal

    def get_transaction_item_id(self):
        """Return the deal id"""
        return self.deal.id

    def is_product(self):
        """Return if this is a product, since it isn't return 0"""
        return 0
    
    def get_description(self):
        """Get the description of the deal"""
        return "%i %s / $%.2f" % (self.deal.product_count, self.product.name,
                                self.deal.deal_price) 
