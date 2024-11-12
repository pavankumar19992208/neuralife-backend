from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
import pyodbc
from pydantic import BaseModel
import random
import string
import mysql.connector

class SchoolRegistration(BaseModel):
    SCHOOL_ID: str
    D_NO: str
    STREET: str
    AREA: str
    CITY: str
    DISTRICT: str
    STATE: str
    PIN_CODE: str
    GEO_TAG: str
    SCHOOL_NAME: str
    SYLLABUS_TYPE: str
    ADH_NAME: str
    ADH_MOBILE: str
    ADH_EMAIL: str
    SCHOOL_LOGO: str  # Add SCHOOL_LOGO field

sch_router = APIRouter()

@sch_router.post("/schregister")
async def register_school(school: SchoolRegistration):
    PASSWORD = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    db = get_db1()
    cursor = db.cursor()

    # Create tables if they do not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schools (
        SCHOOL_ID VARCHAR(50) PRIMARY KEY,
        SCHOOL_NAME VARCHAR(100),
        SYLLABUS_TYPE VARCHAR(50),
        ADH_NAME VARCHAR(100),
        ADH_MOBILE VARCHAR(15),
        ADH_EMAIL VARCHAR(100),
        PASSWORD VARCHAR(50),
        SCHOOL_LOGO VARCHAR(255)  # Add SCHOOL_LOGO field
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS address (
        ID VARCHAR(50) PRIMARY KEY,
        MOBILE VARCHAR(15),
        D_NO VARCHAR(50),
        STREET VARCHAR(100),
        AREA VARCHAR(100),
        CITY VARCHAR(100),
        DISTRICT VARCHAR(100),
        STATE VARCHAR(100),
        PIN_CODE VARCHAR(10),
        GEO_TAG VARCHAR(100)
    )
    """)

    # Insert into schools table
    cursor.execute(
        "INSERT INTO schools (SCHOOL_ID, SCHOOL_NAME, SYLLABUS_TYPE, ADH_NAME, ADH_MOBILE, ADH_EMAIL, PASSWORD, SCHOOL_LOGO) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (school.SCHOOL_ID, school.SCHOOL_NAME, school.SYLLABUS_TYPE, school.ADH_NAME, school.ADH_MOBILE, school.ADH_EMAIL, PASSWORD, school.SCHOOL_LOGO)
    )

    # Insert into address table
    cursor.execute(
        "INSERT INTO address (ID, MOBILE, D_NO, STREET, AREA, CITY, DISTRICT, STATE, PIN_CODE, GEO_TAG) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (school.SCHOOL_ID, school.ADH_MOBILE, school.D_NO, school.STREET, school.AREA, school.CITY, school.DISTRICT, school.STATE, school.PIN_CODE, school.GEO_TAG)
    )

    db.commit()

    return {"SCHOOL_ID": school.SCHOOL_ID, "PASSWORD": PASSWORD}
