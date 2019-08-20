#!/usr/bin/python
"""Register for POS system"""
import Tkinter
import tkSimpleDialog
import tkFont
import tkMessageBox
import sqlite3
from functools import partial
import time
import abscale
import ScaleError
import CartEntry
import tables
import receipt
import ReadSettings
import DatabaseConnect
import MySQLdb
import datetime
import sys
import read_category_order


#from __future__ import print_function
CART_RIGHT = False       
TRANSACTION_TOTAL_TABLE = "farm_register_transactiontotal"
TRANSACTION_ITEM_TABLE = "farm_register_transactionitem"
EMPLOYEE_DISCOUNT_RATE = .75

def add_frame(master, f_width, f_height, background_color, row, column):
    """Add a frame to the master with various attributes"""
    new_frame = Tkinter.Frame(master, width=f_width, height=f_height, \
                            background=background_color, borderwidth=3)
    new_frame.grid_propagate(0)
    new_frame.grid(row=row, column=column)
    return new_frame


def clear_frame(frame):
    """Clear a frame"""
    for widget in frame.grid_slaves():
        # Changed from grid_forget() to grid_remove() because forget doesn't delete
        widget.grid_remove()
        widget.destroy()


class Register:
    diagnostic_mode = False
    """The basic component of our register, should be MVC'd if possible"""
    def disable_everything(self):
        """Disable everything so that you have to finish what you are currently doing"""
        self.set_state_everything(self.master_frame, "disabled")

    def enable_everything(self):
        """Enable everything after you have finished doing something"""
        self.set_state_everything(self.master_frame, "normal")
        
    def set_state_everything(self, widget, state):
        """Set the state of a widget, either disabled or normal (enabled)"""
        try:
            widget.configure(state=state)
        except Tkinter.TclError:
            pass
        for child in widget.winfo_children():
            self.set_state_everything(child, state)

    def lock_window(self, window):
        """Lock a window so that you must finish what you are doing"""
        print "Locking Buttons"
        window.transient(self.master_frame)
        window.protocol("WM_DELETE_WINDOW", partial(self.unlock_window, window))
        self.disable_everything()
        
    def simple_lock(self):
        """Lock everything"""
        self.disable_everything()
        
    def simple_unlock(self):
        """Unlock everything"""
        self.enable_everything()
        #self.update_info_from_database()
        self.update_category_frame()
        self.update_products_frame()
        
    def unlock_window(self, window=None):
        """Unlock the window when you are done doing everything"""
        print "Unlocking buttons"
        self.enable_everything()
        if window is not None:
            window.destroy()


    #def get_current_deal_price(self, deal_id):
    #    """Get the price of the newest deal"""
    #    matching_deal_prices = [x for x in self.deal_prices if x.id == deal_id]
    #    current_deal = max(matching_deal_prices, key=lambda x: x.timestamp)
    #    return current_deal.price

    def update_info_from_database(self):
        """Update the products, categories, items, and product_categories"""
        print "Updating info from database\n"
        # original_table_names = ["items", "products", "categories", "product_categories", "product_price", "deal", "deal_price"]
        django_table_names = ["farm_register_item","farm_register_product","farm_register_category", "farm_register_productcategory","farm_register_productprice", "farm_register_deal", "farm_register_dealprice"]
        ITEM, PROD, CAT, PROD_CAT, PROD_PRICE, DEAL = range(6)
        
        tables_used = django_table_names
        
        old_items = self.items
        old_products = self.products
        old_categories = self.categories
        old_prod_cats = self.prod_cats
        old_prod_prices = self.prod_prices
        old_deals = self.deals
        
        try:
            cursor = self.products_db_cursor
            cursor.execute("SELECT * FROM %s" % tables_used[ITEM])
            # Empty all lists if we get a valid connection
            self.items = []
            self.products = []
            self.categories = []
            self.prod_cats = []
            self.prod_prices = []
            self.deals = []

            for item_row in cursor:
                self.items.append(tables.Item(item_row))
                    
            cursor.execute("SELECT * FROM %s" % tables_used[PROD])
            for product_row in cursor:
                self.products.append(tables.Product(product_row))
    
            cursor.execute("SELECT * FROM %s" % tables_used[CAT])
            for category_row in cursor:
                self.categories.append(tables.Category(category_row))
                
            cursor.execute("SELECT * FROM %s" % tables_used[PROD_CAT])
            for product_category_row in cursor:
                # Not Used but in there
                prod_cat_id = product_category_row[0]
                prod = product_category_row[1]
                cat = product_category_row[2]
                self.prod_cats.append([prod, cat])
            
            cursor.execute("SELECT * FROM %s" % tables_used[PROD_PRICE])
            for product_price_row in cursor:
                self.prod_prices.append(tables.ProductPrice(product_price_row))
            
            cursor.execute("SELECT * FROM %s" % tables_used[DEAL])
            for deal_row in cursor:
                self.deals.append(tables.Deal(deal_row))
        
            compare_lists = [old_items == self.items, \
                old_products == self.products, \
                old_categories == self.categories, \
                old_prod_cats == self.prod_cats, \
                old_prod_prices == self.prod_prices, \
                old_deals == self.deals, \
                ]
                # If everything is the same, then return True, otherwise it isn't the same, return False
            #print compare_lists
            if reduce(lambda x,y: x and y, compare_lists):   
                return True
            else:
                return False
            
        except sqlite3.OperationalError as op_error:
            print "sqlite3: Unable to read database, make sure path is correct. Details below:"
            print op_error
        except MySQLdb.OperationalError as mysql_op_error:
            print "mysql: Unable to read database, make sure path is correct. Details below:"
            print mysql_op_error
                        

    def update_products_frame(self):
        """Updates the buttons in the product frame"""
        clear_frame(self.items_frame)
        product_ids = []        
        for product_category in self.prod_cats:
            category = product_category[1]
            if category == self.current_category_id:
                product_ids.append(product_category[0])
        
        
        ordered_product_row = 0
        ordered_product_col = 0
        #print product_ids
        if self.diagnostic_mode: 
            # Get all products even if disabled
            enabled_products = [p for p in self.products if p.id in product_ids]
        else:
            enabled_products = [p for p in self.products if p.id in product_ids and p.enabled]
        
        #print enabled_products
        
        #for product in self.products:
        #    if product.id in product_ids:
        #        if product.enabled:
        if self.current_category_id in self.category_order_dict:
            current_category_order = self.category_order_dict[self.current_category_id]
        else:
            current_category_order = []
        for row in current_category_order:
            ordered_product_col = 0
            for product_id in row:
                if product_id == -1: 
                    # Skipping a column for special code
                    ordered_product_col += 1
                else:
                    # get product from enabled products if it is in there, otherwise skip
                    enabled_product = [p for p in enabled_products if p.id == product_id]
                    if len(enabled_product) > 0:
                        enabled_product = enabled_product[0]
                        # remove the product so you don't add it at the end as well    
                        enabled_products = [p for p in enabled_products if p.id != product_id]    
                        # now add button
                        product_button = self.create_product_button(enabled_product)
                        product_button.grid(row=ordered_product_row, column=ordered_product_col)
                        ordered_product_col += 1
                    #else:
                        #print "Couldn't find id %i in enabled ids for category %i" % (product_id, self.current_category_id)
                        
            ordered_product_row += 1
            
        product_index = 0
        for product in enabled_products:
           
           product_button = self.create_product_button(product)
           prod_row = (product_index / self.products_column_width) + ordered_product_row
           prod_col = product_index % self.products_column_width
           product_button.grid(row=prod_row, column=prod_col)
           product_index += 1

    def create_product_button(self, product):
        product_button = Tkinter.Button(self.items_frame)
        product_price = self.get_product_price(product.id)
       # How the product is displayed in the product frame
        if product.is_premarked:
            if self.diagnostic_mode:
                button_text = "P_id=%i\n%s\nPremarked" %(product.id, product.name)
            else:
                button_text = "%s\n\nPremarked" % (product.name)
        else:
            if self.diagnostic_mode:
                button_text = "P_id=%i\n%s\n$%.2f" % (product.id, product.name, product_price)
                current_deal = self.find_most_recent_deal(product.id)
                if current_deal is not None:
                    button_text += "\nDeal: %i / %.2f" % (current_deal.product_count, current_deal.deal_price)
            else:
                button_text = "%s\n\n$%.2f" % (product.name, product_price)
        if product.is_by_weight:
            button_text += "/lb"
       
        #print "Product" + str(product)
        deal = self.find_most_recent_deal(product.id)
        # What to show if there is a deal
        #if deal is not None:
        #    deal_price = deal.deal_price
        #    button_text += "\n%i / $%.2f" % (deal.product_count, deal_price)
            
        product_button.config(text=button_text, width=self.products_button_width, height=self.products_button_height)
        product_button.config(font=self.product_font, wraplength=130)
        product_button.config(command=partial(self.add_to_cart, product))
        # -- Trying to keep track of destroyed buttons
        #product_button.bind("<Destroy>", lambda x: sys.stdout.write("Destroyed product button widget " + str(x)))
        # -- 
        try:
            product_button.config(background=product.color)
        except:
            tkMessageBox.showerror("Color not allowed", "The color %s for product %s is not allowed, check spelling" % (product.color, product.name))
        return product_button
        
    def get_product_deal(self, product_id):
        """Get a deal for the product"""
        for deal in self.deals:
            if deal.product_id == product_id:
                return deal
        return None

    def update_category_frame(self):
        """Updates the categories in the category frame"""        
        clear_frame(self.category_frame)
        category_index = 0
        print str(self.categories[0])
        for category in [c for c in self.categories if c.enabled]:
            cat_button = Tkinter.Button(self.category_frame, wraplength=80)
            try:
                cat_button.config(background=category.color)
            except:
                    tkMessageBox.showerror("Color not allowed", "The color %s for category %s is not allowed, check spelling" % (category.color, category.name))
            cat_button.config(text=category.name, height=self.categories_button_height, width=self.categories_button_width)
            cat_button.config(command=partial(self.change_category, category.id))
            cat_button.config(font=self.category_font)
            cat_button.config(wraplength=120)
            cat_row = category_index / self.categories_column_width
            cat_col = category_index % self.categories_column_width
            cat_button.grid(row=cat_row, column=cat_col)
            category_index += 1

    def change_category(self, category_id):
        """Change the current category"""
        if self.current_category_id == category_id:
            return
        else:
            self.current_category_id = category_id
            # Changing categories was calling database everytime, slowing things way down
            #if self.update_info_from_database() == False:
            #    self.update_category_frame()
            self.update_products_frame()

    def clear_cart(self):
        """Remove all items from cart"""
        self.cart = []
        self.update_cart()

    def get_weight(self):
        """Get weight from scale or if not connected from dialog"""
        if self.scale is None: 
            weight = tkSimpleDialog.askfloat("Weight Entry", "Weight (lbs):")
        else:
            try:
                weight = self.scale.get_weight()
            except ScaleError.ScaleError as e:
                print "Error reading scale, enter weight manually"
                print e
                weight = tkSimpleDialog.askfloat("Weight Entry", "Weight (lbs):")
        return weight

    def get_product_price(self, product_id):    
        """Get the price of a product, if there are multiple, only use the newest active one"""
        matching_prod_prices = [x for x in self.prod_prices if x.id == product_id]
        newest_price = max(matching_prod_prices, key=lambda x: x.timestamp) 
        return newest_price.price

    def add_to_cart(self, product):
        """Add a product entry into cart"""
        if len(self.cart) == 0:
            self.start_time = time.time()
                
        product_price = self.get_product_price(product.id)
        print "Added a %s" % product.name
        print "Price: %.2f" % product_price
        if product.is_by_weight:
            #print "Bought by weight, must pop up or read scale"
            weight = self.get_weight()
            if weight is not None:
                cart_entry = CartEntry.ProductCartEntry(product, product_price, weight)
                self.cart.append(cart_entry)
        elif product.is_premarked:
            # get price
            premarked_price = tkSimpleDialog.askfloat("Premarked Price", "Price:")
            if premarked_price is not None:
                cart_entry = CartEntry.ProductCartEntry(product, 1, premarked_price )
                self.cart.append(cart_entry)
        else:
            # """Product not by weight"""
            if self._shift_is_pressed:
               amount = tkSimpleDialog.askinteger("Adding how many?", "Amount:")
               if amount is None:
                  print "Tried to add nothing, returning"
                  return
            else:
               amount = 1
               
            found = False
            for cart_index in range(len(self.cart)):
                if isinstance(self.cart[cart_index], CartEntry.ProductCartEntry):
                    if self.cart[cart_index].product.id == product.id:
                        found = True
                        self.cart[cart_index].add_some(amount)
            if not found: 
                cart_entry = CartEntry.ProductCartEntry(product, product_price, amount)
                self.cart.append(cart_entry)
                #if self.is_shift_pressed():
                #    self.change_cart_amount(len(self.cart) - 1)
                #print "Added cart item"
                
        self.update_cart()

    def delete_item(self, cart_row):
        """Delete an item from cart"""
        self.cart.pop(cart_row)
        print "Deleted an item " + str(datetime.datetime.now())
        self.update_cart()
    
    def update_cart(self):
        """Update the cart with all current items"""
        self.update_cart_items()
        self.update_cart_totals()

    def find_most_recent_deal(self, product_id):
        product_deals = [d for d in self.deals if product_id == d.product_id]
        if len(product_deals) == 0:
            return None
        else:
            # Return most recent deal if it is enabled
            #print product_deals[0]
            most_recent_deal = max(product_deals, key=lambda x: x.timestamp)
            if most_recent_deal.enabled:
                return most_recent_deal
            else:
                return None
            
    def update_cart_items(self):
        """Update the items in the cart, taking into account deals"""
        clear_frame(self.cart_items_frame)
        # --- EXPERIMENTAL
        # clear_frame(self.secondary_cart_items_frame)
        # --- END EXP
        text_headers = ["Product","", "Amount", "Unit price","Price", "Delete"]
        for text_headers, text_index in zip(text_headers, range(len(text_headers))):
            header_label = Tkinter.Label(self.cart_items_frame)
            header_label.config(text=text_headers, width=12, justify=Tkinter.LEFT)
            header_label.grid(row=0, column=text_index)
            
            # --- EXPERIMENTAL
            
            # sec_header_label = Tkinter.Label(self.secondary_cart_items_frame)
            # sec_header_label.config(text=text_headers, width=12, justify=Tkinter.LEFT)
            # sec_header_label.grid(row=0, column = text_index)
            
            # --- END EXPERIMENTAL
                
        new_cart = []
        for cart_item in self.cart:
            if isinstance(cart_item, CartEntry.ProductCartEntry):
            #Check for deals
                # Find newest deal
                most_recent_deal = self.find_most_recent_deal(cart_item.product.id)
                new_cart.append(cart_item)
                if most_recent_deal is not None:
                    number_deals = cart_item.get_amount() / most_recent_deal.product_count 
                    if number_deals > 0:           
                        new_cart.append( CartEntry.DealCartEntry(cart_item.product, most_recent_deal, most_recent_deal.deal_price, number_deals))
                    
        self.cart = new_cart
        #print self.cart
        cart_row = 0
        for cart_item in self.cart:
            #End deal check
            self.add_cart_item_labels(self.cart_items_frame, cart_item, cart_row)
            
            # EXPERIMENTAL 
            # self.add_cart_item_labels(self.secondary_cart_items_frame, cart_item, cart_row)
            # END EXP
            cart_row += 1

    def add_cart_item_labels(self, frame, cart_item, cart_row):
        """Add labels to all items in the cart"""
        
        self.cart_item_labels_width = 18
        name_label = Tkinter.Label(frame, width=self.cart_item_labels_width, anchor=Tkinter.W, justify=Tkinter.LEFT, bg=self.values_dict["cart_items_frame_color"])
        # Doubled the cart item label width
        name_label.config(text=cart_item.get_description(), font=self.cart_item_font)
        name_label.grid(row=cart_row + 1, column=0, columnspan=2)
        
        
        
        if isinstance(cart_item, CartEntry.ProductCartEntry):
            amount_button = Tkinter.Button(frame, anchor=Tkinter.CENTER)
            unit_price_label = Tkinter.Label(frame, anchor=Tkinter.W, bg=self.values_dict["cart_items_frame_color"])
            # config unit price label
            if cart_item.product.is_by_weight or cart_item.product.is_premarked:
                amount_button.config(text="%.2f" % cart_item.get_amount())
                if cart_item.product.is_by_weight:
                    unit_price_label.config(text="%.2f / lb" % cart_item.price_per)
                else:
                    unit_price_label.config(text="Premarked")
            else:
                amount_button.config(text="%i" % cart_item.get_amount())
                unit_price_label.config(text="%.2f each" % cart_item.price_per)
                
            amount_button.config(command=partial(self.change_cart_amount, cart_row), font=self.cart_item_font)
            amount_button.grid(row=cart_row + 1, column=2)
            unit_price_label.config(font=self.cart_item_font)
            unit_price_label.grid(row=cart_row + 1, column=3)
            
        else:
            amount_label = Tkinter.Label(frame, anchor=Tkinter.CENTER, bg=self.values_dict["cart_items_frame_color"])
            amount_label.config(text="%i" % cart_item.get_amount(), font=self.cart_item_font)
            amount_label.grid(row=cart_row + 1, column=2)
            
            unit_price_label = Tkinter.Label(frame, anchor=Tkinter.W, bg=self.values_dict["cart_items_frame_color"])
            unit_price_label.config(text="%.2f" % cart_item.deal.deal_price)
            unit_price_label.config(font=self.cart_item_font)
            unit_price_label.grid(row=cart_row + 1, column=3)
        
        price_label = Tkinter.Label(frame, anchor=Tkinter.W, bg=self.values_dict["cart_items_frame_color"])
        price_label.config(text="%.2f" % cart_item.price(), font=self.cart_item_font)
        price_label.grid(row=cart_row + 1, column=4)
        
        if isinstance(cart_item, CartEntry.ProductCartEntry):
            delete_button = Tkinter.Button(frame, anchor=Tkinter.W, )
            delete_button.config(text="X", font=self.cart_item_font)
            delete_button.config(command=partial(self.delete_item, cart_row))
            delete_button.grid(row=cart_row + 1, column=5)

    def update_cart_totals(self):
        """Update the totals of all items in the cart"""
        clear_frame(self.totals_frame)
        #clear_frame(self.secondary_totals_frame)
        
        totals_font = tkFont.Font(family="Tahoma", size=20)
        totals_font_bold = tkFont.Font(family="Tahoma", size=20, weight='bold')
        
        total, sub, ed_tax, non_ed_tax = self.get_total_price()
       
        for frame in [self.totals_frame, ]: #self.secondary_totals_frame]:
            #total_label = Tkinter.Label(frame, text="Total", anchor=Tkinter.W, font=totals_font)
            #total_label.grid(row=5, column=0)
            
            #total_value = Tkinter.Label(frame, text="%.2f" % total, anchor=Tkinter.E, font=totals_font)
            #total_value.grid(row=5, column=1)



            total_label = Tkinter.Label(frame, text="Total", anchor=Tkinter.W, width=15, font=totals_font_bold)
            total_label.config(background="white")
            total_label.grid(row=0, column=0)
            
            total_value = Tkinter.Label(frame, text="%.2f" % total, anchor=Tkinter.E, width=15, font=totals_font_bold)
            total_value.config(background="white")
            total_value.grid(row=0, column=1)
            
            subtotal_label = Tkinter.Label(frame, text="Subtotal", anchor=Tkinter.W, width=15, font=totals_font)
            subtotal_label.grid(row=1, column=0)

            subtotal_value = Tkinter.Label(frame, text="%.2f" % sub, anchor=Tkinter.E, width=15, font=totals_font)
            subtotal_value.grid(row=1, column=1)
            
            ed_tax_label = Tkinter.Label(frame, text="Edible Tax", anchor=Tkinter.W, width=15, font=totals_font)
            ed_tax_label.grid(row=2, column=0)
            
            ed_tax_value = Tkinter.Label(frame, text="%.2f" % ed_tax, anchor=Tkinter.E, width=15, font=totals_font)
            ed_tax_value.grid(row=2, column=1)
            
            non_ed_tax_label = Tkinter.Label(frame, text="Non Edible Tax", anchor=Tkinter.W, width=15, font=totals_font)
            non_ed_tax_label.grid(row=3, column=0)
            
            non_ed_tax_value = Tkinter.Label(frame, text="%.2f" % non_ed_tax, anchor=Tkinter.E, width=15, font=totals_font)
            non_ed_tax_value.grid(row=3, column=1)
        
            employee_discount_button = Tkinter.Button(frame, text="Employee Discount", command=self.employee_discount, width=15, height=1)
            employee_discount_button.config(font=totals_font_bold)
            employee_discount_button.grid(row=4, column=0)


    def receipt_print(self, trans_number, transaction_type):
        """Send the receipt to the printer"""        
        total, subtotal, tax_edible, tax_non_edible = self.get_total_price()
        receipt_info = receipt.ReceiptInfo(trans_number, 
                total, subtotal, tax_edible, tax_non_edible, 
                self.edible_tax_rate, self.nonedible_tax_rate, transaction_type)
        receipt.print_receipt(self.cart, receipt_info, self.receipt_chars_per_inch)
        
    def add_products_frame(self, f_height, b_color):
        """Add the products frame to the register window"""
        row = self.products_frames
        column = 0
        self.products_frames += 1
        return add_frame(self.products_frame, self.products_width, f_height, b_color, row, column)

    def add_cart_frame(self, f_height, b_color):
        """Add the cart frame to the register window"""
        row = self.cart_frames
        column = 0
        self.cart_frames += 1
        return add_frame(self.cart_frame, self.cart_width, f_height, b_color, row, column)    
    
    # --- EXP
    def add_secondary_cart_frame(self, f_height, b_color):
        """Add the secondary cart frame to the secondary window"""
        row = self.secondary_cart_frames
        column = 0
        self.secondary_cart_frames += 1
        print "Adding to secondary cart frame row %i column %i, height %i" % (row, column, f_height)
        return add_frame(self.secondary_cart, self.cart_width, f_height, b_color, row, column)
    # --- EXP
    
    def update_debug_frame(self):
        """Adds options for changing what the transactions go into"""
        
        #r1 = Tkinter.Radiobutton(self.debug_frame, text="Grove", variable=self.radio_variable, value=0)
        #r2 = Tkinter.Radiobutton(self.debug_frame, text="Naples 3rd St", variable=self.radio_variable, value=1)
        #r3 = Tkinter.Radiobutton(self.debug_frame, text="Marco Market", variable=self.radio_variable, value=2)
        #r4 = Tkinter.Radiobutton(self.debug_frame, text="Naples Davis", variable=self.radio_variable, value=3)
        #r5 = Tkinter.Radiobutton(self.debug_frame, text="Bonita", variable=self.radio_variable, value=4)
        
        #col = 0
        #for r in [r1,r2,r3,r4,r5]:
        #    r.grid(row=0, column=col)
        #    col = col + 1
    
    def update_payment_frame(self):
        """Adds the payment frame buttons to the register window"""
        
        payment_font = tkFont.Font(weight=tkFont.BOLD, size=self.payment_font_size)
        cash_button = Tkinter.Button(self.payment_type_frame, text="Cash", command=self.cash_pay, width=self.payment_button_width, height=self.payment_button_height)
        cash_button.config(font=payment_font)
        cash_button.grid(row=0, column=0)
    
        credit_button = Tkinter.Button(self.payment_type_frame, text="Credit Card", command=self.credit_pay, width=self.payment_button_width, height=self.payment_button_height)
        credit_button.config(font=payment_font)
        credit_button.grid(row=0, column=1)
    
        check_button = Tkinter.Button(self.payment_type_frame, text="Check", command=self.check_pay, width=self.payment_button_width, height=self.payment_button_height)
        check_button.config(font=payment_font)
        check_button.grid(row=0, column=2)
    
        no_sale_button = Tkinter.Button(self.payment_type_frame, text="No Sale", command=self.no_sale, width=self.payment_button_width, height=self.payment_button_height)
        no_sale_button.config(font=payment_font) 
        no_sale_button.grid(row=0, column=3)
        


    def employee_discount(self):
        """Not yet implemented"""
        self.employee_discount_enabled = not self.employee_discount_enabled
        self.update_cart()
  

    def no_sale(self):
        if self._shift_is_pressed:
            tkMessageBox.showwarning("Diagnostic Mode", "Entering Diagnostic Mode")
            self.diagnostic_mode = True
        elif self._ctrl_is_pressed:
            tkMessageBox.showwarning("Receipt Read Mode", "Entering Receipt Read Mode")
            self.receipt_mode = True
        else:
            print "NO SALE PRESSED " + str(datetime.datetime.now())
            receipt.print_no_sale()
        
    def cash_pay(self):
        """Called when payed with cash"""
        total, _, _, _ = self.get_total_price()
        if total > 0.00:
            self.input_cash_amount_dialog()
        else:
            tkMessageBox.showwarning("Total is zero", "Total is zero, did you mean No Sale?")
            
    def input_cash_amount_dialog(self):
        """Get the amount of cash the customer pays with"""
        
        change_window = Tkinter.Toplevel(self.master_frame)
        change_window.title("Cash Amount")
        
        self.lock_window(change_window)
        
        amount_index = 0
        bold_font = tkFont.Font(family="Arial", size=12, weight=tkFont.BOLD)
        for amount in [50.00, 20.00, 15.00, 10.00, 5.00]:
            amount_button = Tkinter.Button(change_window, text="$%.2f" % amount)
            amount_button.config(command=partial(self.submit_cash_amount, False, amount, change_window))
            amount_button.config(width=self.values_dict["cash_button_width"], height=self.values_dict["cash_button_height"])
            amount_button.config(font=bold_font)
            amount_button.grid(row=0, column=amount_index)
            amount_index += 1
        # Exact change button
        exact_button = Tkinter.Button(change_window, text="Exact")
        total, _, _, _ = self.get_total_price()
        exact_button.config(command=partial(self.submit_cash_amount, False, total, change_window))
        exact_button.config(width=self.values_dict["cash_button_width"], height=self.values_dict["cash_button_height"])
        exact_button.config(font=bold_font)
        exact_button.grid(row=0, column=amount_index)
        
        amount_label = Tkinter.Label(change_window, text="Enter Amount:")
        amount_label.grid(row=1, column=0)
        cash_var = Tkinter.StringVar()
        amount_entry = Tkinter.Entry(change_window, textvariable=cash_var, width=8)
        entry_font = tkFont.Font(size=20, weight=tkFont.BOLD)
        amount_entry.config(font=entry_font)
        amount_entry.bind("<Return>", partial(self.submit_cash_amount_enter, True, cash_var, change_window))
        amount_entry.bind("<KP_Enter>", partial(self.submit_cash_amount_enter, True, cash_var, change_window))
        amount_entry.grid(row=1, column=1, columnspan=2)
        amount_entry.focus_set()
        ok_button = Tkinter.Button(change_window, text="OK", command=partial(self.submit_cash_amount, True, cash_var, change_window))
        ok_button.config(width=self.values_dict["cash_button_width"], font=bold_font)
        ok_button.grid(row=1, column=3)
        cancel_button = Tkinter.Button(change_window, text="Cancel", command=partial(self.unlock_window, change_window))
        cancel_button.config(width=self.values_dict["cash_button_width"], font=bold_font)
        cancel_button.grid(row=1, column=4)
        
    def submit_cash_amount_enter(self, is_string_var, amount, window_to_close, _):
        """Called when the enter key is pressed"""
        self.submit_cash_amount(is_string_var, amount, window_to_close)
           
    def submit_cash_amount(self, is_string_var, amount, window_to_close):
        """Called when the amount of cash given is selected"""
        try:
            if is_string_var:
                cash_amount = float(amount.get())
            else:
                cash_amount = amount
        except ValueError:
            print amount
            tkMessageBox.showwarning("Cash not right", "Can't convert amount to a number")     
        else:
            total, _, _, _ = self.get_total_price()
            window_to_close.destroy()
            self.finish_transaction("CASH")
            self.display_change_amount(total, cash_amount)
            self.clear_cart()
            print "CASH SALE PRESSED " + str(datetime.datetime.now())
        finally:
            self.unlock_window(window_to_close)
            
    def display_change_amount(self, total, cash_amount):
        """Display the amount of change to give to the customer"""
        change = cash_amount - total
        tkMessageBox.showinfo("Change", "Change: $%.2f" % change)
        
    def credit_pay(self):
        """Called when payment is credit card"""
        total, _, _, _ = self.get_total_price()
        if total > 0.00:
            self.finish_transaction("CREDIT CARD")
            self.simple_lock()
            tkMessageBox.showinfo("Credit Card Payment", "Total: $%.2f" % (total))
            self.simple_unlock()
            self.clear_cart()
            print "CREDIT SALE PRESSED " + str(datetime.datetime.now())
        else:
            tkMessageBox.showwarning("Total is zero", "Total is zero, did you mean No Sale?")
            
    def check_pay(self):
        """Called when payment is check"""    
        total, _, _, _ = self.get_total_price()
        if total > 0.00:
            self.finish_transaction("CHECK")
            self.simple_lock()
            tkMessageBox.showinfo("Check Payment", "Total: $%.2f" % (total))
            self.simple_unlock()
            self.clear_cart()
            print "CHECK SALE PRESSED " + str(datetime.datetime.now())
        else:
            tkMessageBox.showwarning("Total is zero", "Total is zero, did you mean No Sale?")
            
    def finish_transaction(self, transaction_type):
        """Logs the transaction and prints receipt, clears cart for next transaction"""
        trans_number = self.log_transaction(transaction_type)
        if trans_number != -1:
            self.receipt_print(trans_number, transaction_type)
        self.employee_discount_enabled = False    

    def log_transaction(self, transaction_type):
        """Log the transaction into the database"""
        total, sub, ed_tax, non_ed_tax = self.get_total_price()
        #timestamp = timeformat.get_timestamp_string()
        cashier = self.cashierVar.get()
        time_to_finish = int(time.time() - self.start_time)
        #location = self.get_market_location()
        
        timestamp = str(datetime.datetime.now())
        insert_values = (total, sub, ed_tax, non_ed_tax, timestamp, cashier, time_to_finish, transaction_type)
        print insert_values
        print "Logging transaction"
        sql = "INSERT INTO " + TRANSACTION_TOTAL_TABLE + " VALUES (NULL,%f,%f,%f,%f,'%s','%s',%i,'westmont','%s');" % insert_values
        self.products_db_cursor.execute(sql)
        trans_number = self.products_db_connect.insert_id()
        
        sql_statements = []
        for entry in self.cart:
            entry_insert_values = (trans_number, entry.is_product(), entry.get_transaction_item_id(), entry.get_amount())
            sql_statements.append("INSERT INTO " + TRANSACTION_ITEM_TABLE + " VALUES (NULL,%i,%i,%i,%f);" % entry_insert_values)
        
        if trans_number == -1:
            print "Saving temporary to file"
            transaction_file = open("UnsavedTrans/" + str(datetime.datetime.now()) + str(cashier) + ".sql", "w")
            sql_text = reduce(lambda x,y: x+"\n"+y, sql_statements)
            transaction_file.write(sql_text)
            transaction_file.close()
        else:
            for sql_statement in sql_statements:
                self.products_db_cursor.execute(sql_statement)
            self.products_db_connect.commit()
        
            # save to file 
        return trans_number
        
    def get_subtotal_price(self):
        """Determine the price of all items in the cart"""
        subtotal =  0.0 + sum(cart_item.price() for cart_item in self.cart)
        if self.employee_discount_enabled:
            return EMPLOYEE_DISCOUNT_RATE * subtotal 
        else:
            return subtotal

    def get_total_price(self):
        """Get the sub total plus all applicable taxes"""
        sub = self.get_subtotal_price()
        ed_tax, non_ed_tax = self.get_tax_amount()
        return sub + ed_tax + non_ed_tax, sub, ed_tax, non_ed_tax

    def get_tax_amount(self):
        """Get edible and non edible taxes on items"""
        tax_edible = 0.0
        tax_non_edible = 0.0
        for cart_item in self.cart:
            if cart_item.product.is_nonedible:
                tax_non_edible += cart_item.price() * self.nonedible_tax_rate
            else:
                tax_edible += cart_item.price() * self.edible_tax_rate
        return tax_edible, tax_non_edible

    def change_cart_amount(self, cart_row):
        """Change the amount of a product entry in a cart"""
        print 'Changing amount of item in cart'
        self.simple_lock()
        if self.cart[cart_row].product.is_by_weight:
            amount = tkSimpleDialog.askfloat("Enter new weight", "Weight:")
        elif self.cart[cart_row].product.is_premarked:
            amount = tkSimpleDialog.askfloat("Enter new amount", "Amount:")
        else:
            amount = tkSimpleDialog.askinteger("Enter new amount", "Amount:")
        self.simple_unlock()
            
        if amount is None:
            print "Canceled"
        elif amount == 0:
            print "Can't update amount to 0, use delete key instead"
        else:
            print "Updated amount " + str(amount)
            self.cart[cart_row].change_amount(amount)
        self.update_cart()

    def read_products_categories_constants(self):
        # Product
        self.product_font_size = int(self.values_dict["product_font_size"])
        self.products_column_width = int(self.values_dict["products_column_width"])
        self.products_button_width = int(self.values_dict["products_button_width"])
        self.products_button_height = int(self.values_dict["products_button_height"])

        # Category        
        self.category_font_size = int(self.values_dict["category_font_size"])
        self.categories_column_width = int(self.values_dict["categories_column_width"])
        self.categories_button_width  = int(self.values_dict["categories_button_width"])
        self.categories_button_height = int(self.values_dict["categories_button_height"])
        
        # Payment buttons
        self.payment_font_size = int(self.values_dict["payment_font_size"])
        self.payment_button_width = int(self.values_dict["payment_button_width"])
        self.payment_button_height = int(self.values_dict["payment_button_height"])
        
        # Cart item
        self.cart_item_font_size = int(self.values_dict["cart_item_font_size"])
        
        # Cart totals
        self.cart_total_font_size = int(self.values_dict["cart_total_font_size"])
        
        # Set up fonts
        self.product_font = tkFont.Font(size=self.product_font_size, weight=tkFont.BOLD)
        self.category_font = tkFont.Font(size=self.category_font_size, weight=tkFont.BOLD)
        self.payment_font = tkFont.Font(size=self.payment_font_size, weight=tkFont.BOLD)
        self.cart_item_font = tkFont.Font(size=self.cart_item_font_size, weight=tkFont.BOLD)
        self.total_font = tkFont.Font(size=self.cart_total_font_size, weight=tkFont.BOLD)

    def _shift_pressed(self, event):
        self._shift_is_pressed = True
        # Debug print 
        print "Shift press"

    def _shift_released(self, event):
        self._shift_is_pressed = False
        # Debug print
        print "Shift release" 
    
    def _ctrl_pressed(self, event):
        self._ctrl_is_pressed = True
        print "Ctrl Pressed"
        
    def _ctrl_released(self, event):
        self._ctrl_is_pressed = False
        print "Ctrl Released"
        
    def __init__(self, master, init_file_name, scale):
        """Initiate all variables for the register program"""
        try:
            init_file = open(init_file_name)
        except IOError:
            print "Couldn't find initiation file for configuring register"
        self.employee_discount_enabled = False
        self.values_dict = ReadSettings.get_values_from_init_file(init_file)
        print self.values_dict
        # Radio variable for 
        #self.radio_variable = Tkinter.IntVar()
        #self.radio_variable.set(0) # Set to grove initially
        self.scale = scale
        self.master = master
        self.cashierVar = Tkinter.StringVar()
        self.cashierVar.set(self.values_dict["register_name"])
        self.cart = []    
        self.items = []
        self.products = []
        self.categories = []
        self.prod_cats = []
        self.prod_prices = []
        self.deals = []
        self.deal_prices = []
        self.current_category_id = 1
        self.start_time = time.time()
        
        cursor, conn = DatabaseConnect.connect(self.values_dict)
        # Early exit if can't connect to database
        if cursor is None:
            tkMessageBox.showwarning("Database Error", "Could not connect to database, check errors on terminal")
            new_ip_address = tkSimpleDialog.askstring("Manual ip address entry", "Enter ip address of host to connect to (127.0.0.1 if can't connect to network)")
            
            if new_ip_address is not None:
               self.values_dict["database_path"] = new_ip_address 
               cursor, conn = DatabaseConnect.connect(self.values_dict)
               print "Tried connecting to manual ip address " + new_ip_address
               if cursor is None:
                  tkMessageBox.showwarning("Manual ip entry failure", "Failed to connect to manual ip address, closing")
                  master.destroy()
                  return
            else:
               master.destroy()
               return
        
        # read product ordering in category preferences
        
        self.category_order_dict = read_category_order.read_category_order()

        self.products_db_cursor = cursor
        self.products_db_connect = conn
         
        self.update_info_from_database()
        self.transaction_number = 0
        self.read_products_categories_constants()
                
        application_height = int(self.values_dict["application_height"])
        application_width = int(self.values_dict["application_width"])
        self.edible_tax_rate = float(self.values_dict["edible_tax_rate"])
        self.nonedible_tax_rate = float(self.values_dict["nonedible_tax_rate"])
        
        self.products_width = int(self.values_dict["products_width"])
        self.cart_width = int(self.values_dict["cart_width"])
        
        # Inside products frame, eventually read these from a file
        information_height = int(self.values_dict["information_height"])
        categories_height = int(self.values_dict["categories_height"])
        items_height = int(self.values_dict["items_height"])
        debug_height = int(self.values_dict["debug_height"])
                
        #Inside cart frame
        cart_info_height = int(self.values_dict["cart_info_height"])
        cart_items_height = int(self.values_dict["cart_items_height"])
        totals_height = int(self.values_dict["totals_height"])
        payment_type_height = int(self.values_dict["payment_type_height"])
        #Receipt info
        self.receipt_chars_per_inch = int(self.values_dict["receipt_chars_per_inch"])
        print self.receipt_chars_per_inch
        
        self.master.resizable(False,False)
        
        self.products_frames = 0
        self.cart_frames = 0
        self.master_frame = Tkinter.Frame(master)
       
        self.master_frame.grid()
        
        # EXP ---
        #self.secondary_cart = Tkinter.Toplevel(master)
        #self.secondary_cart.title("Customer Cart View")
        #self.secondary_cart.resizable(False,False)
        #self.secondary_cart.protocol("WM_DELETE_WINDOW", self.secondary_cart.iconify)
        #self.secondary_cart.grid()
        #self.secondary_cart_frames = 0
        # EXP ---
        
        #Removed functionality, possibly read later but not unless necessary
        self._shift_is_pressed = False
        self._ctrl_is_pressed = False
        self.master_frame.bind_all("<Shift_L>", self._shift_pressed)
        self.master_frame.bind_all("<KeyRelease-Shift_L>", self._shift_released)
        self.master_frame.bind_all("<Control_L>", self._ctrl_pressed)
        self.master_frame.bind_all("<KeyRelease-Control_L>", self._ctrl_released)        
                
        assert application_height == information_height + categories_height + items_height + debug_height
        assert application_height == cart_info_height + cart_items_height + totals_height + payment_type_height
        assert application_width == self.products_width + self.cart_width
        if CART_RIGHT:
            products_frame_column = 0
            cart_frame_column = 1
        else:
            products_frame_column = 1
            cart_frame_column = 0
        self.products_frame = add_frame(self.master_frame, self.products_width, application_height, "gray", 0, products_frame_column)
        self.cart_frame = add_frame(self.master_frame, self.cart_width, application_height, "gray", 0, cart_frame_column)
    
        # Products frame additions
        self.information_frame = self.add_products_frame(information_height, self.values_dict["information_frame_color"])
        self.category_frame = self.add_products_frame(categories_height, self.values_dict["categories_frame_color"])
        self.items_frame = self.add_products_frame(items_height, self.values_dict["items_frame_color"])
        self.debug_frame = self.add_products_frame(debug_height, self.values_dict["debug_frame_color"])

        # Cart frame additions
        self.payment_type_frame = self.add_cart_frame(payment_type_height, self.values_dict["payment_type_frame_color"])
        self.cart_info_frame = self.add_cart_frame(cart_info_height, self.values_dict["cart_info_frame_color"])
        self.cart_items_frame = self.add_cart_frame(cart_items_height, self.values_dict["cart_items_frame_color"])
        self.totals_frame = self.add_cart_frame(totals_height, self.values_dict["totals_frame_color"])
        
        # EXP ---
        # Secondary cart additions
        # self.secondary_cart_items_frame = self.add_secondary_cart_frame(cart_items_height, self.values_dict["cart_items_frame_color"])
        # self.secondary_totals_frame = self.add_secondary_cart_frame(totals_height, "gray")
        # EXP ---
        
        #self.update_admin_frame()
        self.update_category_frame()
        self.update_products_frame()
        self.update_cart()
        self.update_payment_frame()            
        self.update_debug_frame()
        
def startRegister():
    """Start the register, connect to scale"""
    import os
    init_file_name = "settings.txt"
    root = Tkinter.Tk()
    root.title("Register")
    
    scale = None
    possible_connection = False
    for usb_number in range(4):
        scale_path = "/dev/ttyUSB%i" % usb_number
        if os.path.exists(scale_path):
            possible_connection = True
            scale = abscale.ABScale(scale_path)
            if scale.is_scale_connected():
                break
            else:
                scale = None
    if scale is None:
        if not possible_connection:
            tkMessageBox.showwarning("Scale Not Connected", "Scale is not connected.\
                Check connections and restart if scale is present")
        else:
            tkMessageBox.showwarning("Scale Not Connected", "Scale is not connected \
                but a possible scale is detected. Check permissions and restart if scale is present")
    
    Register(root, init_file_name, scale)        
    root.mainloop()
        
if __name__ == "__main__":
    startRegister()
    
