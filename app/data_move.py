# from fastapi import APIRouter, HTTPException, Depends
# import pyodbc
# from pydantic import BaseModel
# from typing import Optional
# import mysql.connector
# # def get_db():
# #     conn_str = (
# #         r'DRIVER={ODBC Driver 18 for SQL Server};'
# #         r'SERVER=tcp:p2ptrail.database.windows.net,1433;'
# #         r'DATABASE=p2p_trail;'
# #         r'UID=p2padmin;'
# #         r'PWD=Techworks@1234'
# #     )
# #     cnxn = pyodbc.connect(conn_str)
# #     return cnxn
# def get_db():
#     conn_str = (
#         r'DRIVER={ODBC Driver 18 for SQL Server};'
#         r'SERVER=tcp:p2pdata.database.windows.net,1433;'
#         r'DATABASE=p2p_data;'
#         r'UID=p2padmin1;'
#         r'PWD=techworks@1234'
#     )
#     cnxn = pyodbc.connect(conn_str)
#     return cnxn
# def get_db1():
#     config = {
#         'user': 'if0_36200926',
#         'password': 'bSJ2pXZiaM',
#         'host': 'sql110.infinityfree.com',
#         'database': 'if0_36200926_p2pdata',
#         'raise_on_warnings': True
#     }

#     cnxn = mysql.connector.connect(**config)
#     return cnxn

# cursor=get_db().cursor()
# cursor1=get_db1().cursor()




# class Teacher(BaseModel):
#     SCHOOL_ID: str
#     TEACHER_ID: str
#     TEACHER_NAME: str
#     QUALIFICATION: str
#     AADHAR_NO: Optional[str]
#     TEACHER_MOBILE: str
#     TEACHER_EMAIL: str
#     DOC_ID: Optional[str]
#     PASSWORD: Optional[str]

# def fetch_data_from_source_db(cursor):
#     cursor.execute("SELECT * FROM [dbo].[teachers]")
#     rows = cursor.fetchall()
#     data = [Teacher(SCHOOL_ID=row[0], TEACHER_ID=row[1], TEACHER_NAME=row[2], QUALIFICATION=row[3], AADHAR_NO=row[4], TEACHER_MOBILE=row[5], TEACHER_EMAIL=row[6], DOC_ID=row[7], PASSWORD=row[8]) for row in rows]
#     return data

# def insert_data_into_target_db(cursor, data):
#     for row in data:
#         cursor.execute("INSERT INTO teachers (SCHOOL_ID, TEACHER_ID, TEACHER_NAME, QUALIFICATION, AADHAR_NO, TEACHER_MOBILE, TEACHER_EMAIL, DOC_ID, PASSWORD) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
#                        (row.SCHOOL_ID, row.TEACHER_ID, row.TEACHER_NAME, row.QUALIFICATION, row.AADHAR_NO, row.TEACHER_MOBILE, row.TEACHER_EMAIL, row.DOC_ID, row.PASSWORD))
#     cursor.commit()
# data = fetch_data_from_source_db(cursor)

# insert_data_into_target_db(cursor1, data)