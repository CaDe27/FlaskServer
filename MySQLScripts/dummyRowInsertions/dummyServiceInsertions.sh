#!/bin/bash

CONFIG_FILE="./config.json"

# Extracting the password from the config.json
DB_name=$(jq -r '.database.name' "$CONFIG_FILE")
DB_user=$(jq -r '.database.user' "$CONFIG_FILE")


# MySQL command to create table
mysql -u "$DB_user" -p -D "$DB_name" -e "INSERT INTO services (service_name, description) VALUES
('BestHamburguers', 'restaurant'),
('BestWings', 'restaurant'),
('butcher shop', 'butcher shop'),
('Dairy store', 'Dairy store'),
('Green grocer', 'Green grocer'),
('Chocolate shop', 'Chocolate shop');
"


