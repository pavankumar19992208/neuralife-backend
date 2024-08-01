from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
import pyodbc
from pydantic import BaseModel
import random
import string
from typing import List

class TeacherRegistration(BaseModel):
    SCHOOL_ID: str
    TEACHER_NAME: str
    QUALIFICATION: str
    AADHAR_NO: str
    TEACHER_MOBILE: str
    TEACHER_EMAIL: str
    DOC_ID: str
    D_NO: str
    STREET: str
    AREA: str
    CITY: str
    DISTRICT: str
    STATE: str
    PIN_CODE: str
    SUBJECTS: List[str]
    TEACHER_PIC: str  # Add TEACHER_PIC field
    TEACHER_ID: str
tea_router = APIRouter()

@tea_router.post("/tregister")
async def register_teacher(teacher: TeacherRegistration, db=Depends(get_db1)):
    # Generate TEACHER_ID and PASSWORD
    PASSWORD = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    cursor = db.cursor()

    # Create tables if they don't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        SCHOOL_ID VARCHAR(255),
        TEACHER_ID VARCHAR(255) PRIMARY KEY,
        TEACHER_NAME VARCHAR(255),
        QUALIFICATION VARCHAR(255),
        AADHAR_NO VARCHAR(255),
        TEACHER_MOBILE VARCHAR(255),
        TEACHER_EMAIL VARCHAR(255),
        DOC_ID VARCHAR(255),
        PASSWORD VARCHAR(255),
        TEACHER_PIC TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS address (
        ID VARCHAR(255),
        MOBILE VARCHAR(255),
        D_NO VARCHAR(255),
        STREET VARCHAR(255),
        AREA VARCHAR(255),
        CITY VARCHAR(255),
        DISTRICT VARCHAR(255),
        STATE VARCHAR(255),
        PIN_CODE VARCHAR(255),
        PRIMARY KEY (ID, MOBILE)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        TEACHER_ID VARCHAR(255),
        SUBJECT VARCHAR(255),
        PRIMARY KEY (TEACHER_ID, SUBJECT)
    )
    """)

    # Insert into teachers table
    cursor.execute(
        "INSERT INTO teachers (SCHOOL_ID, TEACHER_ID, TEACHER_NAME, QUALIFICATION, AADHAR_NO, TEACHER_MOBILE, TEACHER_EMAIL, DOC_ID, PASSWORD, TEACHER_PIC) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (teacher.SCHOOL_ID, teacher.TEACHER_ID, teacher.TEACHER_NAME, teacher.QUALIFICATION, teacher.AADHAR_NO, teacher.TEACHER_MOBILE, teacher.TEACHER_EMAIL, teacher.DOC_ID, PASSWORD, teacher.TEACHER_PIC)
    )

    # Insert into address table
    cursor.execute(
        "INSERT INTO address (ID, MOBILE, D_NO, STREET, AREA, CITY, DISTRICT, STATE, PIN_CODE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (teacher.TEACHER_ID, teacher.TEACHER_MOBILE, teacher.D_NO, teacher.STREET, teacher.AREA, teacher.CITY, teacher.DISTRICT, teacher.STATE, teacher.PIN_CODE)
    )

    # Insert into subjects table
    for subject in teacher.SUBJECTS:
        cursor.execute(
            "INSERT INTO subjects (TEACHER_ID, SUBJECT) VALUES (%s, %s)",
            (teacher.TEACHER_ID, subject)
        )

    db.commit()

    return {"message": "Teacher registration successful", "TEACHER_ID": teacher.TEACHER_ID, "PASSWORD": PASSWORD}