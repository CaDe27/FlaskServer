#!/bin/bash

CONFIG_FILE="../../config.json"

# Extracting the password from the config.json
DB_name=$(jq -r '.database.name' "$CONFIG_FILE")
DB_user=$(jq -r '.database.user' "$CONFIG_FILE")

mysql -u root -p -e "
CREATE DATABASE IF NOT EXISTS $DB_name;
    -- the @'localhost' indicates that this user can only connect from the same
    -- machine where the database exists. 
    CREATE USER IF NOT EXISTS '$DB_user'@'localhost' IDENTIFIED BY '$DB_password';
    GRANT ALL PRIVILEGES ON $DB_name.* TO '$DB_user'@'localhost';
    FLUSH PRIVILEGES;
"