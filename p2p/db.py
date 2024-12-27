import mysql.connector
from mysql.connector import Error

def get_db1():
    try:
        connection = mysql.connector.connect(
            host='34.72.131.9',
            user='root',  # replace with your MySQL username
            password='devtest@123',  # replace with your MySQL password
            database='neuraLife'  # replace with your MySQL database name
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


def get_db2():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # replace with your MySQL username
            password='Amma@9502',  # replace with your MySQL password
            database='p2p_data'  # replace with your MySQL database name
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
