import sqlite3
import MySQLdb

def connect(values_dict):
    if values_dict["database_format"].strip() == "sqlite":
        products_db_connect = sqlite3.connect(values_dict["database_path"])
    elif values_dict["database_format"].strip() == "mysql":
        try:
            db_user = "root"
            db_user_pw = "dave"
            db_name = "products"
            db_host = values_dict["database_path"]
            products_db_connect = MySQLdb.connect(db_host, db_user, db_user_pw, db_name)
            
        except MySQLdb.DatabaseError as e:
            print "Failed to connect to mysql database, Database Error, check path"
            print e
            return
        except sqlite3.DatabaseError as e:
            print "Failed to connect to sqlite database"
            print e
            return
        except:
            print "General Database Error"
            return
    else:
        print "Unknown Database format, unable to connect"
        return
    
    products_db_cursor = products_db_connect.cursor()
    return products_db_cursor, products_db_connect