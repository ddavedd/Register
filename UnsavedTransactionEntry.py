import ReadSettings
import DatabaseConnect
import os

def get_max_transaction_number(cursor):   
    cursor.execute("SELECT max(transaction_id) FROM transaction_total")        
    for max_transaction_number_row in cursor:
        max_trans_number = max_transaction_number_row[0]
        
    if max_trans_number is None:
        max_trans_number = 1
    else:
        return max_trans_number + 1
    
try:
    init_file_name = "settings.txt"
    init_file = open(init_file_name)
except:
    print "Couldn't open settings.txt"
    
values_dict = ReadSettings.get_values_from_init_file(init_file)
try:
    cursor, conn = DatabaseConnect.connect(values_dict)   
except:
    print "Error connecting to database"
# Insert into database
for f in os.listdir("UnsavedTrans"):
    max_trans_num = get_max_transaction_number(cursor)
    file_path = os.getcwd() + "/UnsavedTrans/" + f
    open_f = open(file_path)
    transaction_statements = open_f.read()
    open_f.close()
    clean_statements = transaction_statements.replace("-1,", str(max_trans_num) + ",")
    print clean_statements
    for l in clean_statements.split("\n"):
        cursor.execute(l)
    conn.commit()
    os.remove(file_path)
print "Finished."