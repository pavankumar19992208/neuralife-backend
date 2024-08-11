import pandas as pd
import mysql.connector
from mysql.connector import errorcode
import os

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Define the relative path to the CSV file
csv_file_path = os.path.join(script_dir, 'student.csv')

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)

# Replace NaN values with an empty string
df = df.fillna('')

# Connect to the MySQL database
try:
    conn = get_db1()
    cursor = conn.cursor()


    # Insert the data into the address table
    for index, row in df.iterrows():
        insert_query = """
        INSERT INTO students (SCHOOL_ID, STUDENT_ID, STUDENT_NAME, GRADE, SECTION, AADHAR_NO, GUARDIAN_NAME, RELATION, GUARDIAN_MOBILE, GUARDIAN_EMAIL, DOC_ID, PASSWORD, STUDENT_PIC)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, tuple(row))

    # Commit the transaction
    conn.commit()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
finally:
    cursor.close()
    conn.close()

print("Data imported successfully into the address table.")