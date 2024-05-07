#!/bin/bash

CONFIG_FILE="../../config.json"

# Extracting the password from the config.json
DB_name=$(jq -r '.database.database' "$CONFIG_FILE")
DB_user=$(jq -r '.database.user' "$CONFIG_FILE")
DB_password=$(jq -r '.database.password' "$CONFIG_FILE")

# MySQL command to create table
mysql -u "$DB_user" -p -D "$DB_name" -e "
CREATE TABLE IF NOT EXISTS services (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS http_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    datetime TIMESTAMP NOT NULL,
    caller_service_id INT,
    receiver_service_id INT,
    status_code INT,
    latency_ms INT,
    FOREIGN KEY (caller_service_id) REFERENCES services(service_id),
    FOREIGN KEY (receiver_service_id) REFERENCES services(service_id)
);
-- Creates the index for the http requests table.
CREATE INDEX idx_datetime ON http_requests(datetime);
"