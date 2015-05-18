import sqlite3
import MySQLdb
#from subprocess import check_output, call

def connect(values_dict):
    if values_dict["database_format"].strip() == "sqlite":
        products_db_connect = sqlite3.connect(values_dict["database_path"])
    elif values_dict["database_format"].strip() == "mysql":
        try:
            db_user = "root"
            db_user_pw = "dave"
            db_name = "thefarm"
            db_host = values_dict["database_path"]
            products_db_connect = MySQLdb.connect(db_host, db_user, db_user_pw, db_name)
            
        except MySQLdb.DatabaseError as e:
            print "Failed to connect to mysql database, Database Error, check path"

#            nmap_out = check_output(["nmap","-sP","10.1.10.1/24"])
#            print call(["grep","-o", "10.1.10.*", nmap_out]) 
            print e
            return None, None
        except sqlite3.DatabaseError as e:
            print "Failed to connect to sqlite database"
            print e
            return None, None
        except:
            print "General Database Error"
            return None, None
    else:
        print "Unknown Database format, unable to connect"
        return None, None
    
    products_db_cursor = products_db_connect.cursor()
    return products_db_cursor, products_db_connect
