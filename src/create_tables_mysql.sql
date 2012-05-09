USE products;
CREATE TABLE categories (category_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, category_name TEXT);
CREATE TABLE deal (deal_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, product_id INT, product_count INT, enabled INT);
CREATE TABLE deal_price (deal_id INT, deal_price FLOAT, timestamp TEXT);
CREATE TABLE items (item_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, item_name TEXT);
CREATE TABLE product_categories (product_id INT, category_id INT);
CREATE TABLE product_price (product_id INT, prod_price FLOAT, timestamp TEXT);
CREATE TABLE products (product_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, prod_name TEXT, prod_by_weight INT, item_id INT, item_count INT, tax_rate_nonedible INT, enabled INT, is_premarked INT);
CREATE TABLE transaction_item (transaction_id INT, is_product INT, product_id INT, product_amount FLOAT);
CREATE TABLE transaction_total (transaction_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, total FLOAT, subtotal FLOAT, edible_tax FLOAT, nonedible_tax FLOAT, timestamp TEXT, cashier TEXT, transaction_time INT);

