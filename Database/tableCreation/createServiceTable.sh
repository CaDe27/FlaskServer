#!/bin/bash

CONFIG_FILE="./config.json"

# Extracting the password from the config.json
DB_name=$(jq -r '.database.database' "$CONFIG_FILE")
DB_user=$(jq -r '.database.user' "$CONFIG_FILE")


# MySQL command to create table
mysql -u "$DB_user" -p -D "$DB_name" -e "
CREATE TABLE IF NOT EXISTS services (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    description TEXT
);
"