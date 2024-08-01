from pydantic import BaseModel
import random
import string
from fastapi import APIRouter, HTTPException
from db import get_db1
import mysql.connector

st_router = APIRouter()

class Student(BaseModel):
    SCHOOL_ID: str
    STUDENT_NAME: str
    GRADE: str
    SECTION: str
    AADHAR_NO: str
    GUARDIAN_NAME: str
    RELATION: str
    GUARDIAN_MOBILE: str
    GUARDIAN_EMAIL: str
    DOC_ID: str
    D_NO: str
    STREET: str
    AREA: str
    CITY: str
    DISTRICT: str
    STATE: str
    PIN_CODE: str
    STUDENT_PIC: str  # New field for profile picture URL
    STUDENT_ID: str

@st_router.post("/st_register")
async def register_student_endpoint(student: Student):
    data = student.dict()
    cnxn = get_db1()
    cursor = cnxn.cursor()

    # Create students table if it doesn't exist
    create_students_table_query = """
    CREATE TABLE IF NOT EXISTS students (
        SCHOOL_ID VARCHAR(50),
        STUDENT_ID VARCHAR(50) PRIMARY KEY,
        STUDENT_NAME VARCHAR(100),
        GRADE VARCHAR(10),
        SECTION VARCHAR(10),
        AADHAR_NO VARCHAR(20),
        GUARDIAN_NAME VARCHAR(100),
        RELATION VARCHAR(50),
        GUARDIAN_MOBILE VARCHAR(15),
        GUARDIAN_EMAIL VARCHAR(100),
        DOC_ID VARCHAR(50),
        PASSWORD VARCHAR(50),
        STUDENT_PIC VARCHAR(255)  # New column for profile picture URL
    )
    """
    cursor.execute(create_students_table_query)

    # Create address table if it doesn't exist
    create_address_table_query = """
    CREATE TABLE IF NOT EXISTS address (
        ID VARCHAR(50) PRIMARY KEY,
        MOBILE VARCHAR(15),
        D_NO VARCHAR(20),
        STREET VARCHAR(100),
        AREA VARCHAR(100),
        CITY VARCHAR(100),
        DISTRICT VARCHAR(100),
        STATE VARCHAR(100),
        PIN_CODE VARCHAR(10),
        GEO_TAG VARCHAR(50)
    )
    """
    cursor.execute(create_address_table_query)

    # Generate a random password
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

    # Insert into students table
    students_query = """
    INSERT INTO students (SCHOOL_ID, STUDENT_ID, STUDENT_NAME, GRADE, SECTION, AADHAR_NO, GUARDIAN_NAME, RELATION, GUARDIAN_MOBILE, GUARDIAN_EMAIL, DOC_ID, PASSWORD, STUDENT_PIC)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(students_query, (
        data['SCHOOL_ID'], data['STUDENT_ID'], data['STUDENT_NAME'], data['GRADE'], data['SECTION'], data['AADHAR_NO'],
        data['GUARDIAN_NAME'], data['RELATION'], data['GUARDIAN_MOBILE'], data['GUARDIAN_EMAIL'], data['DOC_ID'],
        password, data['STUDENT_PIC']
    ))

    # Insert into address table
    address_query = """
    INSERT INTO address (ID, MOBILE, D_NO, STREET, AREA, CITY, DISTRICT, STATE, PIN_CODE, GEO_TAG)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, '')
    """
    cursor.execute(address_query, (
        data['STUDENT_ID'], data['GUARDIAN_MOBILE'], data['D_NO'], data['STREET'], data['AREA'], data['CITY'],
        data['DISTRICT'], data['STATE'], data['PIN_CODE']
    ))

    cnxn.commit()

    return {"student_id": data['STUDENT_ID'], "password": password}