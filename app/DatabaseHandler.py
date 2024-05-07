import mysql.connector
import time

class DatabaseHandler:
    def __init__(self, config):
        self.config = config

    def get_connection(self):
        return mysql.connector.connect(**self.config)
    
    def get_requests_between(self, start_timestamp, end_timestamp, operation):
        operations = {
            "sum latency": "SUM",
            "min latency": "MIN",
            "max latency": "MAX",
            "average latency": "AVG",
            "count": "COUNT"
        }
        sql_operation = operations.get(operation.lower(), "SUM")
        
        query = f"""
        SELECT caller_service_id, receiver_service_id, 
            CASE 
                WHEN status_code >= 100 AND status_code < 200 THEN 100
                WHEN status_code >= 200 AND status_code < 300 THEN 200
                WHEN status_code >= 300 AND status_code < 400 THEN 300
                WHEN status_code >= 400 AND status_code < 500 THEN 400
                WHEN status_code >= 500 AND status_code < 600 THEN 500
            END AS status_code,
            {sql_operation}(latency_ms) AS latency_ms
        FROM http_requests
        WHERE datetime BETWEEN %s AND %s
        GROUP BY caller_service_id, receiver_service_id, 
                CASE 
                    WHEN status_code >= 100 AND status_code < 200 THEN 100
                    WHEN status_code >= 200 AND status_code < 300 THEN 200
                    WHEN status_code >= 300 AND status_code < 400 THEN 300
                    WHEN status_code >= 400 AND status_code < 500 THEN 400
                    WHEN status_code >= 500 AND status_code < 600 THEN 500
                END;
        """
        with self.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, (start_timestamp, end_timestamp))
                return cursor.fetchall()

    def get_services(self):
        query = f"SELECT service_id, service_name FROM services"
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()

                # Converting list of tuples to a dictionary with the service_id as key and the 
                # service name as the value
                services_dict = {service_id: service_name for service_id, service_name in result}
                return services_dict

    def get_min_datetime(self):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COALESCE(MIN(datetime), NOW()) FROM http_requests;")
                return cursor.fetchone()[0]

    def get_max_datetime(self):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COALESCE(MAX(datetime), NOW()) FROM http_requests;")
                return cursor.fetchone()[0]
