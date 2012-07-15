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
import timeformat
import receipt
import TextHintEntry
import ReadSettings
import DatabaseConnect
import MySQLdb
CART_RIGHT = False       
    


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
        widget.grid_forget()


class Register:
    """The basic component of our register, should be MVC'd if possible"""
    
    def add_category(self):
        """Add a category for labeling products"""
        cat_name = tkSimpleDialog.askstring("New Category", "Category Name:")        
        if cat_name is None:
            print "Canceled category addition"
        elif cat_name.strip() == "":
            print "Empty string category not allowed"
        else:
            category_values = cat_name
            sql_text = "INSERT INTO categories VALUES (NULL, '%s')" % category_values
            print sql_text
            self.products_db_cursor.execute(sql_text)
            self.products_db_connect.commit()
            self.update_info_from_database()
            self.update_category_frame()

    def add_basic_item_dialog(self):
        """Add a basic item that can be tracked into to the database"""
        item_name = tkSimpleDialog.askstring("Add a basic item", "Item Name: ")
        if item_name is None:
            print "Canceled adding item"
        elif item_name.strip() == "":
            print "Can't add an empty string item"
        else:
            clean_item_name = item_name.strip()
            sql_text = "INSERT INTO items VALUES (NULL, '%s')" % clean_item_name
            self.products_db_cursor.execute(sql_text)
            self.products_db_connect.commit()
            self.update_info_from_database()

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
        self.update_info_from_database()
        self.update_category_frame()
        self.update_products_frame()
        
    def unlock_window(self, window=None):
        """Unlock the window when you are done doing everything"""
        print "Unlocking buttons"
        self.enable_everything()
        if window is not None:
            window.destroy()

    def add_deal_dialog(self, window_to_close=None):
        """Add a deal window"""
        if window_to_close is not None:
            window_to_close.destroy()
            
        add_deal_window = Tkinter.Toplevel(self.master)
        add_deal_window.title("Add a deal")
        
        self.lock_window(add_deal_window)
        
        product_names = ["%i %s" % (p.id, p.name) for p in self.products]
        
        product_label = Tkinter.Label(add_deal_window, text="Product:")
        product_label.grid(row=0, column=0)
        
        product_var = Tkinter.StringVar()
        product_option = Tkinter.OptionMenu(add_deal_window, product_var, None, [])
        product_option.grid(row=0, column=1)
        
        product_name_search_entry = TextHintEntry.TextHintEntry(add_deal_window)
        product_name_search_entry.set_option_box_hint_list(product_option, product_var, product_names)
        product_name_search_entry.grid(row=1, column=0)
        
        product_amount_label = Tkinter.Label(add_deal_window, text="Amount of products:")
        product_amount_label.grid(row=2, column=0)
        
        product_amount_entry = Tkinter.Entry(add_deal_window)
        product_amount_entry.grid(row=2, column=1)
        
        deal_price_label = Tkinter.Label(add_deal_window, text="Deal Price:")
        deal_price_label.grid(row=3, column=0)
        
        deal_price_entry = Tkinter.Entry(add_deal_window)
        deal_price_entry.grid(row=3, column=1)
        
        submit_button = Tkinter.Button(add_deal_window, text="Add Deal")
        submit_button.config(command=partial(self.add_deal, product_var, product_amount_entry, deal_price_entry, add_deal_window))
        submit_button.grid(row=4, column=0)

    def add_deal(self, product_var, amount_entry, price_entry, window_to_close):
        """Add a deal to the database"""
        #@todo catch problems in input on all dialogs
        
        product_id = int(product_var.get().split(" ")[0])
        amount = int(amount_entry.get())
        price = float(price_entry.get())
        
        self.unlock_window(window_to_close)
        
        deal_insert_values = (product_id, amount, 1)
        self.products_db_cursor.execute("INSERT INTO deal VALUES (NULL,%i,%i,%i)" % deal_insert_values)
        insert_id = self.products_db_cursor.lastrowid
        timestamp = timeformat.get_timestamp_string()
        deal_price_insert_values = (insert_id, price, timestamp)
        self.products_db_cursor.execute("INSERT INTO deal_price VALUES (%i,%f,'%s')" % deal_price_insert_values)
        self.products_db_connect.commit()
    
        self.update_info_from_database()

    def get_current_deal_price(self, deal_id):
        """Get the price of the newest deal"""
        matching_deal_prices = [x for x in self.deal_prices if x.id == deal_id]
        current_deal = max(matching_deal_prices, key=lambda x: x.timestamp)
        return current_deal.price
    
    def get_deal_price_dict(self):
        """Make a dictionary of prices and deals"""
        deal_price_dict = {}
        for deal in self.deals:
            deal_price_dict[deal.id] = self.get_current_deal_price(deal.id) 
        return deal_price_dict

    def disable_product_dialog(self):
        """Disable a product with this window"""
        disable_product_window = Tkinter.Toplevel(self.master)
        disable_product_window.title("Disable Product")
        
        product_strings = []
        for product in self.products:
            product_string = "%i %s" % (product.id, product.name)
            for product_price in self.prod_prices:
                if product_price.id == product.id:
                    product_string += " $%.2f" % product_price.price
            product_strings.append(product_string)
           
        product_var = Tkinter.StringVar()
        product_label = Tkinter.Label(disable_product_window, text="Product to disable:")
        product_label.grid(row=0, column=0)   
        product_option = Tkinter.OptionMenu(disable_product_window, product_var, None, *product_strings)    
        product_option.grid(row=0, column=1)
        check_variable = Tkinter.IntVar()
        check = Tkinter.Checkbutton(disable_product_window, text="Disable", variable=check_variable)
        check.grid(row=0, column=2)
        submit_changes_button = Tkinter.Button(disable_product_window, text="Submit Changes")
        submit_changes_button.config(command=partial(self.disable_product, product_var, disable_product_window, check_variable)) 
        submit_changes_button.grid(row=1, column=0)

    def disable_product(self, product_var, window_to_close, change_to_var):
        """Disable a product"""
        if change_to_var.get() == 1:
            change = 0
            print "enabled=FALSE"
        else:
            change = 1
            print "enabled=TRUE"
        product_string = product_var.get()
        window_to_close.destroy()
        product_id = int(product_string.split(" ")[0])
        print "Disabling deal with id %i" % product_id
        self.products_db_cursor.execute("UPDATE deal SET enabled=%i WHERE deal_id=%i" % (change, product_id))
        self.products_db_connect.commit()
        self.update_info_from_database()
        self.update_products_frame()
            
    def disable_deal_dialog(self):
        """Disable a deal with this window"""
        disable_deal_window = Tkinter.Toplevel(self.master)
        disable_deal_window.title("Disable Deal")
        products_dict = {}
        for product in self.products:
            products_dict[product.id] = product.name
        deal_price_dict = self.get_deal_price_dict()
        deal_strings = ["%i %s %i / $%.2f" % 
            (deal.id, products_dict[deal.product_id], deal.product_count, deal_price_dict[deal.id]) for deal in self.deals]
        deal_var = Tkinter.StringVar()
        product_label = Tkinter.Label(disable_deal_window, text="Deal to disable:")
        product_label.grid(row=0, column=0)
        
        product_option = Tkinter.OptionMenu(disable_deal_window, deal_var, None, *deal_strings)
        product_option.grid(row=0, column=1)
        
        check_variable = Tkinter.IntVar()
        check = Tkinter.Checkbutton(disable_deal_window, text="Disable", variable=check_variable)
        check.grid(row=0, column=2)
        
        submit_changes_button = Tkinter.Button(disable_deal_window, text="Submit Changes")
        submit_changes_button.config(command=partial(self.disable_deal, deal_var, disable_deal_window, check_variable))
        submit_changes_button.grid(row=1, column=0)

    def disable_deal(self, deal_var, window_to_close, change_to_var):
        """Disable a deal"""
        if change_to_var.get() == 1:
            change = 0
            print "enabled=FALSE"
        else:
            change = 1
            print "enabled=TRUE"
        deal_string = deal_var.get()
        window_to_close.destroy()
        deal_id = int(deal_string.split(" ")[0])
        print "Disabling deal with id %i" % deal_id
        self.products_db_cursor.execute("UPDATE deal SET enabled=%i WHERE deal_id=%i" % (change, deal_id))
        self.products_db_connect.commit()
        self.update_info_from_database()
        self.update_products_frame()
        
    def adjust_deal_amount_price_dialog(self):
        """Adjust the price and amount of a deal"""
        adjust_deal_window = Tkinter.Toplevel(self.master)
        adjust_deal_window.title("Adjust Deal")
        
        self.lock_window(adjust_deal_window)
        
        products_dict = {}
        for product in self.products:
            products_dict[product.id] = product.name
        deal_price_dict = self.get_deal_price_dict()
            
        deal_strings = ["%i %s %i / $%.2f" % (d.id, products_dict[d.product_id], d.product_count, deal_price_dict[d.id]) for d in self.deals]
        deal_var = Tkinter.StringVar()
        
        product_label = Tkinter.Label(adjust_deal_window, text="Deal:")
        product_label.grid(row=0, column=0)
        
        product_option = Tkinter.OptionMenu(adjust_deal_window, deal_var, None, *deal_strings)
        product_option.grid(row=0, column=1)
        
        amount_label = Tkinter.Label(adjust_deal_window, text="Amount:")
        amount_label.grid(row=1, column=0)
        amount_entry = Tkinter.Entry(adjust_deal_window)
        amount_entry.grid(row=1, column=1)
        
        price_label = Tkinter.Label(adjust_deal_window, text="Price:")
        price_label.grid(row=2, column=0)
        price_entry = Tkinter.Entry(adjust_deal_window)
        price_entry.grid(row=2, column=1)
        
        submit_changes_button = Tkinter.Button(adjust_deal_window, text="Submit Changes")
        submit_changes_button.config(command=partial(self.adjust_deal, deal_var, amount_entry, price_entry, adjust_deal_window))
        submit_changes_button.grid(row=3, column=0)

    def adjust_deal(self, deal_var, amount_entry, price_entry, window_to_close):
        """Adjust an existing deal"""
        
        deal_string = deal_var.get()
        amount = amount_entry.get()
        price = price_entry.get()
        
        self.unlock_window(window_to_close)
        
        deal_id = int(deal_string.split(" ")[0])
        price = float(price)
        amount = int(amount)
        timestamp = timeformat.get_timestamp_string()
        self.products_db_cursor.execute("UPDATE deal SET product_count=%i WHERE deal_id=%i" % (amount, deal_id))
        self.products_db_cursor.execute("INSERT INTO deal_price VALUES (%i,%f,'%s')" % (deal_id, price, timestamp))
        self.products_db_connect.commit()
        self.update_info_from_database()

    def add_product_to_database_dialog(self):
        """Create a dialog for adding a product"""
        add_product_window = Tkinter.Toplevel(self.master)
        add_product_window.title("Add Product")
        
        self.lock_window(add_product_window)
        
        item_type_label = Tkinter.Label(add_product_window, text="Item:")
        item_type_label.grid(row=0, column=0)
        
        item_type_var = Tkinter.StringVar()
        item_names = [str(x.id) + " " + x.name for x in self.items]

        item_type_option = Tkinter.OptionMenu(add_product_window, item_type_var, item_type_var.get(), None)
        item_type_option.grid(row=0, column=1)
        
        hint_entry = TextHintEntry.TextHintEntry(add_product_window)
        hint_entry.set_option_box_hint_list(item_type_option, item_type_var, item_names)
        hint_entry.grid(row=0, column=2)
        
        item_amount_label = Tkinter.Label(add_product_window, text="Number of items")
        item_amount_label.grid(row=1, column=0)
        
        item_amount_entry = Tkinter.Entry(add_product_window)
        item_amount_entry.grid(row=1, column=1)
        
        name_label = Tkinter.Label(add_product_window, text="Product Name:")    
        name_label.grid(row=2, column=0)
        name_entry = Tkinter.Entry(add_product_window)
        name_entry.grid(row=2, column=1)
        
        price_label = Tkinter.Label(add_product_window, text="Price")
        price_label.grid(row=3, column=0)
        price_entry = Tkinter.Entry(add_product_window)
        price_entry.grid(row=3, column=1)
        
        by_weight_var = Tkinter.IntVar()
        by_weight_button = Tkinter.Checkbutton(add_product_window, text="By Weight", \
                                            variable=by_weight_var)
        by_weight_button.grid(row=4, column=0)
        
        var_tax_rate = Tkinter.IntVar() 
        tax_rate_option = Tkinter.Checkbutton(add_product_window, text="Non-Edible Tax Rate", variable=var_tax_rate)
        tax_rate_option.grid(row=4, column=1)
        
        is_premarked_var = Tkinter.IntVar()
        is_premarked_button = Tkinter.Checkbutton(add_product_window, text="Is Premarked", variable=is_premarked_var)
        is_premarked_button.grid(row=4, column=2)
        
        add_button = Tkinter.Button(add_product_window, text="Add", command=partial(self.add_product_to_database, name_entry, \
                                                                        price_entry, by_weight_var, item_type_var, \
                                                                        item_amount_entry, var_tax_rate, is_premarked_var, add_product_window))
        add_button.grid(row=5, column=0)
        
    def adjust_price_dialog(self):
        """A dialog for adjusting the price of a product"""
            
        adjust_price_window = Tkinter.Toplevel(self.master)
        adjust_price_window.title("Adjust Price")
        
        price_dict = {}
        for product in self.products:
            price = self.get_product_price(product.id)
            price_dict[product.id] = price
        
        product_names_prices = ["%i %s %.2f %s" % (product.id, product.name,
               price_dict[product.id], product.get_item_ending()) for product in self.products]

        product_to_change_label = Tkinter.Label(adjust_price_window, text="Price to change:")
        product_to_change_label.grid(row=0, column=0)
        
        product_var = Tkinter.StringVar()
        product_option = Tkinter.OptionMenu(adjust_price_window, product_var, None, None)
        product_option.grid(row=0, column=1)

        hint_entry = TextHintEntry.TextHintEntry(adjust_price_window)
        hint_entry.set_option_box_hint_list(product_option, product_var, product_names_prices)
        hint_entry.grid(row=0, column=2)
        
        new_price_label = Tkinter.Label(adjust_price_window, text="Adjusted Price")
        new_price_label.grid(row=2, column=0)
        
        new_price_entry = Tkinter.Entry(adjust_price_window)
        new_price_entry.grid(row=2, column=1)
        
        new_price_commit = Tkinter.Button(adjust_price_window, text="Submit Change", 
            command=partial(self.change_product_price, product_var, new_price_entry, adjust_price_window))
        new_price_commit.grid(row=3, column=0)

    def change_product_price(self, product_var, new_price_entry, window_to_close):
        """Change the product price in the database"""

        
        product_id = int(product_var.get().split(" ")[0])
        price = float(new_price_entry.get().strip())
        timestamp = timeformat.get_timestamp_string()
        window_to_close.destroy()
        price_insert_values = (product_id, price, timestamp)
        print price_insert_values
        print "Changing price of product id %i to %.2f" % (product_id, price)
        self.products_db_cursor.execute("INSERT INTO product_price VALUES (%i,%f,'%s')" % price_insert_values)
        self.products_db_connect.commit()
        self.update_info_from_database()
        self.update_products_frame()

    def add_product_to_category_dialog(self, offset=0, window_to_close=None):
        """A dialog for adding a product to a category"""
        if window_to_close is not None:
            window_to_close.destroy()
        
        prod_cat_window = Tkinter.Toplevel(self.master)
        prod_cat_window.title("Add product to category")
        prod_names = [str(x.id) + " " + x.name for x in self.products]
        cat_names = [str(x.id) + " " + x.name for x in self.categories]
        prod_var = Tkinter.StringVar()
        cat_var = Tkinter.StringVar()
        
        if offset > len(prod_names):
            offset = 0
        current_prod = prod_names[offset:offset+50]
        
        
        prod_option = Tkinter.OptionMenu(prod_cat_window, prod_var, "", *current_prod)    
        prod_option.grid(row=0, column=0)
        cat_option = Tkinter.OptionMenu(prod_cat_window, cat_var, "", *cat_names)
        cat_option.grid(row=0, column=1)
        
        change_products_button = Tkinter.Button(prod_cat_window, text="More Products", command=partial(self.add_product_to_category_dialog, offset+50, prod_cat_window))
        change_products_button.grid(row=1, column=0)
        add_to_cat_button = Tkinter.Button(prod_cat_window, text="Add to Category", command=partial(self.add_product_to_category, prod_var, cat_var))
        add_to_cat_button.grid(row=1, column=1)
        exit_button = Tkinter.Button(prod_cat_window, text="Exit", command=prod_cat_window.destroy)
        exit_button.grid(row=1, column=2)

    def add_product_to_category(self, prod_var, cat_var):
        """Add the specified product to a category"""
        try:
            prod_id = int(prod_var.get().split(" ")[0])
            cat_id = int(cat_var.get().split(" ")[0])
            print "Product id: %i, category id: %i" % (prod_id, cat_id)
        
            self.products_db_cursor.execute("INSERT INTO product_categories VALUES (%i, %i)" % (prod_id, cat_id))
            self.products_db_connect.commit()
            
            self.update_info_from_database()
            self.update_products_frame()
            self.update_category_frame()

        except:
            print "Couldn't get product and/or category"

    def add_product_to_database(self, prod_name, prod_price, prod_by_weight, prod_item, prod_item_amount, tax_rate, is_premarked, window_to_close):
        """Add a new product to the database"""
        try:
            premarked = int(is_premarked.get())
            name = prod_name.get().strip()
            if premarked:    
                price = 0.00
            else:
                price = float(prod_price.get())
            by_weight = int(prod_by_weight.get())
            tax_rate = int(tax_rate.get())
            
            item = int(prod_item.get().split(" ")[0])
            if bool(by_weight):
                item_amount = 0
            else:
                item_amount = int(prod_item_amount.get())
         
            self.unlock_window(window_to_close)
                
            cursor = self.products_db_cursor
            product_insert_values = (name, by_weight, item, item_amount, tax_rate, 1, premarked)
            cursor.execute("INSERT INTO products VALUES (NULL,'%s',%i,%i,%i,%i,%i,%i)" % product_insert_values)
            cursor.execute("SELECT product_id FROM products WHERE prod_name='%s'" % name)
            number_matches = 0
            product_id = None
            for product_row in cursor:
                product_id = product_row[0]
                number_matches += 1
            assert number_matches == 1, "Duplicate or no entry in database, must be fixed!"
            timestamp = timeformat.get_timestamp_string()
            price_insert_values = (product_id, price, timestamp)
            print price_insert_values
            cursor.execute("INSERT INTO product_price VALUES (%i,%f,'%s')" % price_insert_values)
            print "Rows added to product_price: %i" % cursor.rowcount
            
            self.products_db_connect.commit()
            self.update_info_from_database()
            self.update_products_frame()
        except ValueError:
            print "Unable to add a product to the database, error translating values"
        finally:
            window_to_close.destroy()

    def update_info_from_database(self):
        """Update the products, categories, items, and product_categories"""
        # Empty all lists
        self.items = []
        self.products = []
        self.categories = []
        self.prod_cats = []
        self.prod_prices = []
        self.deals = []
        self.deal_prices = []
        
        try:
            cursor = self.products_db_cursor
            cursor.execute("SELECT * FROM items")
            for item_row in cursor:
                self.items.append(tables.Item(item_row))
                    
            cursor.execute("SELECT * FROM products")
            for product_row in cursor:
                self.products.append(tables.Product(product_row))
    
            cursor.execute("SELECT * FROM categories")
            for category_row in cursor:
                self.categories.append(tables.Category(category_row))
                
            cursor.execute("SELECT * FROM product_categories")
            for product_category_row in cursor:
                prod = product_category_row[0]
                cat = product_category_row[1]
                self.prod_cats.append([prod, cat])
            
            cursor.execute("SELECT * FROM product_price")
            for product_price_row in cursor:
                self.prod_prices.append(tables.ProductPrice(product_price_row))
            
            cursor.execute("SELECT * FROM deal")
            for deal_row in cursor:
                self.deals.append(tables.Deal(deal_row))
            
            cursor.execute("SELECT * FROM deal_price")
            for deal_price_row in cursor:
                self.deal_prices.append(tables.DealPrice(deal_price_row))
        
        except sqlite3.OperationalError as op_error:
            print "sqlite3: Unable to read database, make sure path is correct. Details below:"
            print op_error
        except MySQLdb.OperationalError as mysql_op_error:
            print "mysql: Unable to read database, make sure path is correct. Details below:"
            print mysql_op_error
                        
    def update_admin_frame(self):
        """Updates the cashier, as well as adds admin buttons if admin logged in"""
        clear_frame(self.information_frame)
        button_text_function = [#("Login", self.set_cashier),
            ("Add Product", self.add_product_to_database_dialog),
            ("Choose Category", self.add_product_to_category_dialog),
            ("Add Category", self.add_category),
            ("Change Product Price", self.adjust_price_dialog),
            ("Add Basic Item", self.add_basic_item_dialog),
            ("Add Deal", self.add_deal_dialog), 
            ("Adjust Deal", self.adjust_deal_amount_price_dialog),
            #("Enable/Disable Deal", self.disable_deal_dialog),
            #("Enable/Disable Product", self.disable_product_dialog)
            ] 
        
        number_columns = 10
        button_index = 0
        
        for name, function in button_text_function:
            button = Tkinter.Button(self.information_frame, text=name, command=function)
            button.config(width=self.values_dict["admin_button_width"], height=self.values_dict["admin_button_height"])
            button_row = button_index / number_columns
            button_column = button_index % number_columns
            button.grid(row=button_row, column=button_column)
            button_index += 1
            
    def update_products_frame(self):
        """Updates the buttons in the product frame"""    
        clear_frame(self.items_frame)
        product_ids = []        
        for product_category in self.prod_cats:
            category = product_category[1]
            if category == self.current_category_id:
                product_ids.append(product_category[0])
        product_font_size = int(self.values_dict["product_font_size"])
        product_font = tkFont.Font(size=product_font_size, weight=tkFont.BOLD)
        product_index = 0
        print product_ids
        
        
        for product in self.products:
            if product.id in product_ids:
                #if product.enabled:
                product_button = Tkinter.Button(self.items_frame)
                product_price = self.get_product_price(product.id)
                if product.is_premarked:
                    button_text = "%s\n\nPremarked"  % (product.name)
                else:
                    button_text = "%s\n\n$%.2f" % (product.name, product_price)
                if product.is_by_weight:
                    button_text += "/lb"
                
                deal = self.get_product_deal(product.id)
                if deal is not None:
                    deal_price = self.get_current_deal_price(deal.id)
                    button_text += "\n%i / $%.2f" % (deal.product_count, deal_price)
                    
                product_button.config(text=button_text, width=self.products_button_width, height=self.products_button_height)
                product_button.config(font=product_font, wraplength=130)
                product_button.config(command=partial(self.add_to_cart, product))
                prod_row = product_index / self.products_column_width
                prod_col = product_index % self.products_column_width
                product_button.grid(row=prod_row, column=prod_col)
                product_index += 1

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
        for category in self.categories:
            cat_button = Tkinter.Button(self.category_frame)
            cat_button.config(text=category.name, height=self.categories_button_height, width=self.categories_button_width)
            cat_button.config(command=partial(self.change_category, category.id))
            cat_row = category_index / self.categories_column_width
            cat_col = category_index % self.categories_column_width
            cat_button.grid(row=cat_row, column=cat_col)
            category_index += 1

    def change_category(self, category_id):
        """Change the current category"""
        self.current_category_id = category_id
        self.update_info_from_database()
        self.update_category_frame()
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
            except ScaleError.ScaleError:
                print "Error reading scale, enter weight manually"
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
                cart_entry = CartEntry.ProductCartEntry(product, premarked_price, 1)
                self.cart.append(cart_entry)
        else:
            # """Product not by weight"""
            found = False
            for cart_index in range(len(self.cart)):
                if isinstance(self.cart[cart_index], CartEntry.ProductCartEntry):
                    if self.cart[cart_index].product.id == product.id:
                        found = True
                        self.cart[cart_index].add_one()
            if not found: 
                cart_entry = CartEntry.ProductCartEntry(product, product_price, 1)
                self.cart.append(cart_entry)
                #if self.is_shift_pressed():
                #    self.change_cart_amount(len(self.cart) - 1)
                #print "Added cart item"
                
        self.update_cart()

    def delete_item(self, cart_row):
        """Delete an item from cart"""
        self.cart.pop(cart_row)
        self.update_cart()
    
    def update_cart(self):
        """Update the cart with all current items"""
        self.update_cart_items()
        self.update_cart_totals()

    def update_cart_items(self):
        """Update the items in the cart, taking into account deals"""
        clear_frame(self.cart_items_frame)
        text_headers = ["Product", "Amount", "Price", "Delete"]
        for text_headers, text_index in zip(text_headers, range(len(text_headers))):
            header_label = Tkinter.Label(self.cart_items_frame)
            header_label.config(text=text_headers, width=12, justify=Tkinter.LEFT)
            header_label.grid(row=0, column=text_index)
                
        new_cart = []
        for cart_item in self.cart:
            if isinstance(cart_item, CartEntry.ProductCartEntry):
            #Check for deals
                deals = [x for x in self.deals if x.product_id == cart_item.product.id]
                if len(deals) > 0:
                    print "Checking for deals"
                    deal_price_dict = self.get_deal_price_dict()
                    deal = deals[0]
                
                    number_deals = cart_item.get_amount() / deal.product_count            
                    products_left = cart_item.get_amount() % deal.product_count
                    if products_left > 0:
                        new_cart.append(CartEntry.ProductCartEntry(cart_item.product, cart_item.price_per, products_left))
                    if number_deals > 0:
                        found = False
                        for new_cart_item in new_cart:
                            if isinstance(new_cart_item, CartEntry.DealCartEntry) and new_cart_item.deal.id == deal.id:
                                new_cart_item.change_amount(new_cart_item.get_amount() + number_deals)
                                found = True
                        if not found:
                            new_cart.append( CartEntry.DealCartEntry(cart_item.product, deal, deal_price_dict[deal.id], number_deals))
                else:
                    new_cart.append(cart_item)
            else:
                new_cart.append(cart_item)
        
        self.cart = new_cart
        #print self.cart
        cart_row = 0
        for cart_item in self.cart:
            #End deal check
            self.add_cart_item_labels(self.cart_items_frame, cart_item, cart_row)
            cart_row += 1

    def add_cart_item_labels(self, frame, cart_item, cart_row):
        """Add labels to all items in the cart"""
        bold_font = tkFont.Font(size=14, weight=tkFont.BOLD)
        self.cart_item_labels_width = 10
        name_label = Tkinter.Label(frame, anchor=Tkinter.W)
        name_label.config(text=cart_item.get_description(), width=self.cart_item_labels_width, font=bold_font)
        name_label.grid(row=cart_row + 1, column=0)
        
        amount_button = Tkinter.Button(frame, anchor=Tkinter.W, width=self.cart_item_labels_width)
        if cart_item.product.is_by_weight:
            amount_button.config(text="%.2f" % cart_item.get_amount())
        else:
            amount_button.config(text="%i" % cart_item.get_amount())
        amount_button.config(command=partial(self.change_cart_amount, cart_row), font=bold_font)
        amount_button.grid(row=cart_row + 1, column=1)
        
        price_label = Tkinter.Label(frame, anchor=Tkinter.W, width=self.cart_item_labels_width)
        price_label.config(text="%.2f" % cart_item.price(), font=bold_font)
        price_label.grid(row=cart_row + 1, column=2)
        
        delete_button = Tkinter.Button(frame, anchor=Tkinter.W, width=self.cart_item_labels_width)
        delete_button.config(text="X", font=bold_font)
        delete_button.config(command=partial(self.delete_item, cart_row))
        delete_button.grid(row=cart_row + 1, column=3)

    def update_cart_totals(self):
        """Update the totals of all items in the cart"""
        clear_frame(self.totals_frame)
        totals_font = tkFont.Font(family="Arial", size=12)
        totals_bold = tkFont.Font(family="Arial", size=12, weight=tkFont.BOLD)
        total, sub, ed_tax, non_ed_tax = self.get_total_price()
        subtotal_label = Tkinter.Label(self.totals_frame, text="Subtotal", anchor=Tkinter.W, width=15, font=totals_font)
        subtotal_label.grid(row=0, column=0)

        subtotal_value = Tkinter.Label(self.totals_frame, text="%.2f" % sub, anchor=Tkinter.E, width=15, font=totals_font)
        subtotal_value.grid(row=0, column=1)
        
        ed_tax_label = Tkinter.Label(self.totals_frame, text="Edible Tax", anchor=Tkinter.W, width=15, font=totals_font)
        ed_tax_label.grid(row=1, column=0)
        
        ed_tax_value = Tkinter.Label(self.totals_frame, text="%.2f" % ed_tax, anchor=Tkinter.E, width=15, font=totals_font)
        ed_tax_value.grid(row=1, column=1)
        
        non_ed_tax_label = Tkinter.Label(self.totals_frame, text="Non Edible Tax", anchor=Tkinter.W, width=15, font=totals_font)
        non_ed_tax_label.grid(row=2, column=0)
        
        non_ed_tax_value = Tkinter.Label(self.totals_frame, text="%.2f" % non_ed_tax, anchor=Tkinter.E, width=15, font=totals_font)
        non_ed_tax_value.grid(row=2, column=1)
        
        total_label = Tkinter.Label(self.totals_frame, text="Total", anchor=Tkinter.W, width=15, font=totals_bold)
        total_label.grid(row=3, column=0)
        
        total_value = Tkinter.Label(self.totals_frame, text="%.2f" % total, anchor=Tkinter.E, width=15, font=totals_bold)
        total_value.grid(row=3, column=1)

    def receipt_print(self):
        """Send the receipt to the printer"""        
        total, subtotal, tax_edible, tax_non_edible = self.get_total_price()
        receipt_info = receipt.ReceiptInfo(self.transaction_number, 
                total, subtotal, tax_edible, tax_non_edible, 
                self.edible_tax_rate, self.nonedible_tax_rate)
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
    
    def update_payment_frame(self):
        """Adds the payment frame buttons to the register window"""
        
        bold_font = tkFont.Font(weight=tkFont.BOLD, size=11)
        cash_button = Tkinter.Button(self.payment_type_frame, text="Cash", command=self.cash_pay, width=self.payment_button_width, height=self.payment_button_height)
        cash_button.config(font=bold_font)
        cash_button.grid(row=0, column=0)
    
        credit_button = Tkinter.Button(self.payment_type_frame, text="Credit Card", command=self.credit_pay, width=self.payment_button_width, height=self.payment_button_height)
        credit_button.config(font=bold_font)
        credit_button.grid(row=0, column=1)
    
        check_button = Tkinter.Button(self.payment_type_frame, text="Check", command=self.check_pay, width=self.payment_button_width, height=self.payment_button_height)
        check_button.config(font=bold_font)
        check_button.grid(row=0, column=2)
    
        no_sale_button = Tkinter.Button(self.payment_type_frame, text="No Sale", command=self.no_sale, width=self.payment_button_width, height=self.payment_button_height)
        no_sale_button.config(font=bold_font)
        no_sale_button.grid(row=0, column=3)
        
    def no_sale(self):
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
            self.finish_transaction()
            self.display_change_amount(total, cash_amount)
            self.clear_cart()
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
            self.finish_transaction()
            self.simple_lock()
            tkMessageBox.showinfo("Credit Card Payment", "Total: $%.2f" % (total))
            self.simple_unlock()
            self.clear_cart()
        else:
            tkMessageBox.showwarning("Total is zero", "Total is zero, did you mean No Sale?")
            
    def check_pay(self):
        """Called when payment is check"""    
        total, _, _, _ = self.get_total_price()
        if total > 0.00:
            self.finish_transaction()
            self.simple_lock()
            tkMessageBox.showinfo("Check Payment", "Total: $%.2f" % (total))
            self.simple_unlock()
            self.clear_cart()
        else:
            tkMessageBox.showwarning("Total is zero", "Total is zero, did you mean No Sale?")
            
    def finish_transaction(self):
        """Logs the transaction and prints receipt, clears cart for next transaction"""
        self.log_transaction()
        self.receipt_print()
        
    def get_transaction_number(self):
        """Get the number of the next transaction"""
        try:
            self.products_db_cursor.execute("SELECT max(transaction_id) FROM transaction_total")
            max_trans_number = 0
            for max_transaction_number_row in self.products_db_cursor:
                max_trans_number = max_transaction_number_row[0]
            if max_trans_number is None:
                return 1
            else:
                return max_trans_number + 1
        except:
            print "Couldn't connect to database for transaction number"
            return -1
            
    def log_transaction(self):
        """Log the transaction into the database"""
        # Returns -1 if no database connection
        trans_number = self.get_transaction_number()
        # ----- #
        trans_number = -1
        self.transaction_number = trans_number
        total, sub, ed_tax, non_ed_tax = self.get_total_price()
        timestamp = timeformat.get_timestamp_string()
        cashier = self.cashierVar.get()
        time_to_finish = int(time.time() - self.start_time)
        insert_values = (trans_number, total, sub, ed_tax, non_ed_tax, timestamp, cashier, time_to_finish)
        print "Logging transaction"
    
        sql_statements = []
        sql_statements.append("INSERT INTO transaction_total VALUES (%i,%f,%f,%f,%f,'%s','%s',%i);" % insert_values)
        for entry in self.cart:
            entry_insert_values = (trans_number, entry.is_product(), entry.get_transaction_item_id(), entry.get_amount())
            sql_statements.append("INSERT INTO transaction_item VALUES (%i,%i,%i,%f);" % entry_insert_values)
        
        if trans_number == -1:
            print "Saving temporary to file"
            transaction_file = open("UnsavedTrans/" + str(timestamp) + str(cashier) + ".sql", "w")
            sql_text = reduce(lambda x,y: x+"\n"+y, sql_statements)
            transaction_file.write(sql_text)
            transaction_file.close()
        else:
            for sql_statement in sql_statements:
                self.products_db_cursor.execute(sql_statement)
            self.products_db_connect.commit()
        
            # save to file 
            
    def get_subtotal_price(self):
        """Determine the price of all items in the cart"""
        return sum(cart_item.price() for cart_item in self.cart)

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
        #np = NumberPadDialog.NumberPadDialog()
        if self.cart[cart_row].product.is_by_weight:
            amount = tkSimpleDialog.askfloat("Enter new weight", "Weight:")
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

    def set_cashier(self):
        """Set the name of the current cashier"""
        # Should do this from a list in the database
        cashier = tkSimpleDialog.askstring("Cashier Name", "Name:")
        if cashier is None:
            print "Canceled cashier entry"
        elif cashier.strip() == "":
            print "Must be non empty string"
        else:
            self.cashierVar.set(cashier)
        self.update_admin_frame()
 
    def read_products_categories_constants(self):
        self.products_column_width = int(self.values_dict["products_column_width"])
        self.categories_column_width = int(self.values_dict["categories_column_width"])
        
        self.products_button_width = int(self.values_dict["products_button_width"])
        self.products_button_height = int(self.values_dict["products_button_height"])
        
        self.categories_button_width  = int(self.values_dict["categories_button_width"])
        self.categories_button_height = int(self.values_dict["categories_button_height"])
    
    def __init__(self, master, init_file_name, scale):
        """Initiate all variables for the register program"""
        try:
            init_file = open(init_file_name)
        except IOError:
            print "Couldn't find initiation file for configuring register"
        
        self.values_dict = ReadSettings.get_values_from_init_file(init_file)
        print self.values_dict
        
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
        self.products_db_cursor = cursor
        self.products_db_conn = conn
         
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
        
        self.payment_button_width = int(self.values_dict["payment_button_width"])
        self.payment_button_height = int(self.values_dict["payment_button_height"])
        
        self.products_frames = 0
        self.cart_frames = 0
        self.master_frame = Tkinter.Frame(master)
        self.master_frame.grid()

        #Removed functionality, possibly read later but not unless necessary
        #self._shift_is_pressed = False
        #self.master_frame.bind_all("<Shift_L>", self._shift_pressed)
        #self.master_frame.bind_all("<KeyRelease-Shift_L>", self._shift_unpressed)
                
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
        
        self.update_admin_frame()
        self.update_category_frame()
        self.update_products_frame()
        self.update_cart()
        self.update_payment_frame()            

def startRegister():
    """Start the register, connect to scale"""
    init_file_name = "settings.txt"
    root = Tkinter.Tk()
    root.title("Register")
    scale = abscale.ABScale("/dev/ttyUSB0")
    if scale.is_scale_connected():
        reg = Register(root, init_file_name, scale)
    else:
        reg = Register(root, init_file_name, None)        
    root.mainloop()
        
if __name__ == "__main__":
    startRegister()
    