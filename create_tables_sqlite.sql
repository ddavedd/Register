CREATE TABLE categories (category_id INTEGER PRIMARY KEY, category_name TEXT);
CREATE TABLE deal (deal_id INTEGER PRIMARY KEY, product_id INTEGER, product_count INTEGER, enabled INTEGER);
CREATE TABLE deal_price (deal_id INTEGER, deal_price REAL, timestamp TEXT);
CREATE TABLE items (item_id INTEGER PRIMARY KEY, item_name TEXT);
CREATE TABLE product_categories (product_id INTEGER, category_id INTEGER);
CREATE TABLE product_price (product_id INTEGER, prod_price REAL, timestamp TEXT);
CREATE TABLE products (product_id INTEGER PRIMARY KEY, prod_name TEXT, prod_by_weight INTEGER, item_id INTEGER, item_count INTEGER, tax_rate_nonedible INTEGER, enabled INTEGER, is_premarked INTEGER);
CREATE TABLE transaction_item (transaction_id INTEGER, is_product INTEGER, product_id INTEGER, product_amount REAL);
CREATE TABLE transaction_total (transaction_id INTEGER PRIMARY KEY, total REAL, subtotal REAL, edible_tax REAL, nonedible_tax REAL, timestamp TEXT, cashier TEXT, transaction_time INTEGER);
