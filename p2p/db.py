import mysql.connector

def get_db1():
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

def get_db2():
    config = {
        'user': 'if0_36200926',
        'password': 'bSJ2pXZiaM',
        'host': 'sql110.infinityfree.com',
        'database': 'if0_36200926_p2pdata',
        'raise_on_warnings': True
    }

    cnxn = mysql.connector.connect(**config)
    return cnxn
