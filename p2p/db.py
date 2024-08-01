
import pyodbc
import mysql.connector

def get_db():
    conn_str = (
        r'DRIVER={ODBC Driver 18 for SQL Server};'
        r'SERVER=tcp:p2ptrail.database.windows.net,1433;'
        r'DATABASE=p2p_trail;'
        r'UID=p2padmin;'
        r'PWD=Techworks@1234'
    )
    cnxn = pyodbc.connect(conn_str)
    return cnxn


import mysql.connector

def get_db1():
    conn = mysql.connector.connect(
        host="p2ptechworks.cr6yco4g2jh4.eu-north-1.rds.amazonaws.com",
        user="p2p_admin",  # Replace with your RDS username
        password="Amma9502",  # Replace with your RDS password
        database="p2p_data"  # Replace with your RDS database name
    )
    return conn

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
