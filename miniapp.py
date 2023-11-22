from flask import Flask
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

@app.route('/')
def index():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="user",
            password="userP@ssw0rd",
            database="servicesHttpRequests"
        )

        if conn.is_connected():
            return "Connection successful."
        else:
            return "Connection failed."

    except Error as e:
        return f"Error connecting to MySQL Database: {e}"

    finally:
        if conn.is_connected():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
