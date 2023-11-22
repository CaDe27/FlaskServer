import mysql.connector

class DatabaseHandler:
    def __init__(self, config):
        self.config = config

    def get_connection(self):
        return mysql.connector.connect(**self.config)
    
    def get_requests_between(self, start_timestamp, end_timestamp):
        query = f"""
            SELECT * FROM http_requests
            WHERE datetime BETWEEN %s AND %s;
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
                cursor.execute("SELECT MIN(datetime) FROM http_requests;")
                return cursor.fetchone()[0]

    def get_max_datetime(self):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT MAX(datetime) FROM http_requests;")
                return cursor.fetchone()[0]
