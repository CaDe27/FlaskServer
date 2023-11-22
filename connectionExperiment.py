import mysql.connector
from mysql.connector import Error

try:
    # Attempt to establish a connection
    conn = mysql.connector.connect(
        host="localhost",
        user="user",
        password="userP@ssw0rd",
        database="servicesHttpRequests"
    )

    if conn.is_connected():
        print("Connection successful.")
    else:
        print("Connection failed.")

except Error as e:
    print(f"Error connecting to MySQL Database: {e}")

finally:
    # Close the connection if it was successful
    if 'conn' in locals() and conn.is_connected():
        conn.close()
        print("MySQL connection is closed.")
