'''
Created on May 1, 2012

@author: David Smits
'''
import datetime
import subprocess

#def generate_sales_report(self):
    #GenerateSalesReport.generateSalesReport(self.cursor)
#        ("Sales Report", self.generate_sales_report)        

def generateSalesReport(cursor):
    cursor.execute("SELECT * FROM products")
    products = []
    for product_row in cursor:
        products.append([product_row[0], product_row[1], 0.0])
    
    date_string = str(datetime.date.today()).replace("-"," ")
    
    cursor.execute("SELECT min(transaction_id) FROM transaction_total WHERE timestamp >= '%s'" % date_string)
    min_id = 0
    for r in cursor:
        min_id = r[0]
    cursor.execute("SELECT * FROM transaction_item WHERE transaction_id >= %i" % min_id)
    
    transaction_rows = []
    for transaction_row in cursor:
        transaction_rows.append(transaction_row)
    for p in products:
        for t in transaction_rows:
            # If transaction item is a product (could be deal need special case for that later) and ids match
            if t[1]==1 and p[0] == t[2]:
                # Add amount of product
                p[2] = p[2] + t[3]
    name = "SalesReports/SalesReport" + str(datetime.date.today()) + ".csv"
    x = open(name, "w")
    for p in products:
        x.write(p[1] + "," + str(p[2]) + "\n")
    x.close()