#!/bin/bash

CONFIG_FILE="../../config.json"

# Extracting the password from the config.json
DB_name=$(jq -r '.database.database' "$CONFIG_FILE")
DB_user=$(jq -r '.database.user' "$CONFIG_FILE")


# MySQL command to create table
mysql -u "$DB_user" -p -D "$DB_name" -e "INSERT INTO services (service_name, description) VALUES
    ('Ad', 'Handles user ads'),
    ('Cart', 'Handles user items and the quantity of each'), 
    ('Currency', 'Handles currency conversions from USD to other currencys'),
    ('Email', 'Handles emailing user invoices'),
    ('Frontend', 'Handles the user web page'),
    ('Payment', 'Handles user payments'),
    ('Product_Catalog', 'Handles '),
    ('Cart_Redis', 'The redis instance that stores user items and quantities');
"
# ('Users', 'Manages user accounts, profiles, and authentication'),
# ('Products', 'Manages product information for books, music, and electronics'),
# ('Orders', 'Handles order processing, status updates, and history'),
# ('Payments', 'Manages payment processing and invoice generation'),
# ('Inventory', 'Keeps track of stock levels for products'),
# ('Shipping', 'Handles shipping logistics and tracking'),
# ('Recommendations', 'Generates product recommendations based on user behavior and preferences'),
# ('Reviews', 'Manages user reviews for products'),
# ('Promotions','Handles promotional offers and discounts'),
# ('Notifications','Sends notifications to users (e.g., order updates, promotions)'),
# ('Analytics','Analyzes sales, user behavior, and system performance data');"
