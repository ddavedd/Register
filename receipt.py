"""Class for generating receipt and saving/printing it"""
import subprocess
import datetime
import CartEntry

class ReceiptInfo(object):
    """A struct with all the necessary info for the receipt"""
    def __init__(self, transaction_number, total, subtotal, tax_edible, tax_non_edible, tax_rate_edible, tax_rate_nonedible):
        self.transaction_number = transaction_number
        self.total = total
        self.subtotal = subtotal
        self.tax_edible = tax_edible
        self.tax_non_edible = tax_non_edible
        self.tax_rate_edible = tax_rate_edible
        self.tax_rate_non_edible = tax_rate_nonedible

def generate_receipt_text(cart, receipt_info):
    """Generate the text to print for customer receipt"""
    receipt_text = ""
    receipt_text += receipt_info_header()
    receipt_text += receipt_time_transaction(receipt_info)
    receipt_text += receipt_cart(cart, receipt_info)
    receipt_text += receipt_info_footer()
    return receipt_text

def receipt_cart(cart, receipt_info):
    """Gather all information from cart to add to the receipt"""
    text = ""
    for entry in cart:
        if isinstance(entry, CartEntry.ProductCartEntry): 
            if entry.product.is_by_weight:
                text += "%.2f lbs %s x $%.2f/lb = $%.2f\n" % (entry.get_amount(), entry.get_description(), entry.price_per, entry.price() )
            elif entry.product.is_premarked:
                text += "$%.2f %s\n" % (entry.get_amount(), entry.get_description())
            else:
                text += "%i %s x $%.2f = $%.2f\n" % (entry.get_amount(), entry.get_description(), entry.price_per, entry.price())
        else:
            # Otherwise it is a DealCartEntry (3 Spaces) 
            text += "   DISCOUNT %i x %.2f = $%.2f\n" % (entry.get_amount(), entry.price_per, entry.price()) 

    text += "\n"
    text += "Subtotal: %.2f\n" % (receipt_info.subtotal)
    text += "Tax Edible (%.2f%%): $%.2f\n" % (receipt_info.tax_rate_edible * 100, receipt_info.tax_edible)
    text += "Tax Non Edible (%.2f%%): $%.2f\n" % (receipt_info.tax_rate_non_edible * 100, receipt_info.tax_non_edible)
    text += "Total: $%.2f\n" % (receipt_info.total)	
    return text

def receipt_info_header():
    """Information to add to the top of the receipt"""
    text = "The Farm\n34 E 63rd St\nwww.thefarmwestmont.com\n(630)960-3965\n\n"
    #text = "South Naples Citrus Grove\n341 Sabal Palm Road, Naples, FL 34114\nnaplescitrus.com\n(239) 774-3838\n\n"
    return text

def receipt_info_footer():
    """Information to add to the bottom of the receipt"""
    #text = "Thank you for choosing The Farm"
    text = "\n"
    return text

def receipt_time_transaction(receipt_info):
    """Adds cashier name, current time, and transaction number to receipt"""
    current_date = datetime.datetime.now()
    text = current_date.strftime("%B %d, %Y %I:%M") + "\n"
    text += "Transaction #%i\n\n" % receipt_info.transaction_number 
    return text

def print_receipt(cart, receipt_info, receipt_chars_per_inch):
    """Send the receipt to the printer"""	
    text = generate_receipt_text(cart, receipt_info)
    receipt_file_name = "receipts/receipt%s.txt" % receipt_info.transaction_number
    receipt_file = open(receipt_file_name, "w")
    receipt_file.write(text)
    receipt_file.close()
    # send text to printer, in our case, send it to output
    characters_per_inch_option = "-o cpi=%i" % receipt_chars_per_inch
    subprocess.Popen(["lpr", characters_per_inch_option, receipt_file_name])


def print_no_sale():
    text="\n\n\n"
    receipt_file_name = "receipts/blank.txt"
    receipt_file = open(receipt_file_name, "w")
    receipt_file.write(text)
    receipt_file.close()
    
    subprocess.Popen(["lpr", receipt_file_name])
