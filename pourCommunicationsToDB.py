import logging
import time
import mysql.connector
import os
import json
import signal
import sys
import redis

#=============== LOGGING
# Configure logging
logging.basicConfig(level=logging.DEBUG)  
# Create a file handler and set the log file name
log_file_name = 'app.log'
file_handler = logging.FileHandler(log_file_name)
# Configure the format of log messages (optional)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# Add the file handler to the logger
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
#END=============== LOGGING

def exit_handler(sig, frame):
    logger.info('Exiting database insertion process')
    sys.exit(0)
signal.signal(signal.SIGINT, exit_handler)

# Connect to MySQL
def get_mysql_db_connection():
    return mysql.connector.connect(**db_config)

# Connect to Redis
def get_redis_connection():
    return redis.Redis(host=redis_config['host'],
                        port=redis_config['port'],
                        password=redis_config['password'],
                        decode_responses=True)

def insert_to_mysql(data):
    query_template = f"INSERT INTO {table} {'('+', '.join(column_names)+')'} VALUES (%s, %s, %s, %s, %s)"
    for attempt in range(5):
        try:
            with get_mysql_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.executemany(query_template, data)
                    connection.commit()
                    return True
        except mysql.connector.Error as err:
            logger.error(f"Attempt {attempt + 1} failed: {err}")
            time.sleep(1)
    logger.error("All attempts to insert to MySQL failed, rolling back to Redis")
    return False

def fetch_from_redis_and_insert():
    redis_server = get_redis_connection()
    tmp_key = 'tmp_log_queue'
    primary_key = "communications_logs_queue"
    data = []

    item = redis_server.rpoplpush(primary_key, tmp_key)
    while item is not None:
        item_dict = json.loads(item)
        item_tuple = tuple(item_dict[column] for column in column_names)
        data.append(item_tuple)
        item = redis_server.rpoplpush(primary_key, tmp_key)
    
    if data:
        succesful = insert_to_mysql(data)
        if succesful:
            while redis_server.lpop(tmp_key):
                pass
        else:
            while redis_server.rpoplpush(tmp_key, primary_key):
                pass
            logger.error("Unsuccesful insertion to mysql, rolled back to Redis")

# load configuration from file
with open('config.json') as config_file:
    config = json.load(config_file)
    db_config = config['database']
    redis_config = config['redis']

table = "http_requests"
column_names = ('datetime', 'caller_service_id', 'receiver_service_id', 'status_code', 'latency_ms')

time.sleep(20)
while True:
    start_time = time.time()
    fetch_from_redis_and_insert() 
    end_time = time.time()
    execution_time = end_time - start_time 
    sleep_time = max(60 - (end_time - start_time), 0)  # Calculate sleep time, ensuring it's not negative
    logger.debug(f"Execution took {execution_time:.2f} seconds. Sleeping for {sleep_time:.2f} seconds.")
    
    time.sleep(sleep_time)  # Sleep for the remaining time until the next minute
    