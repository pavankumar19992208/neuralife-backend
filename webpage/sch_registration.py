from fastapi import APIRouter, HTTPException
from db import get_db1
from pydantic import BaseModel
import random
import string
import mysql.connector

class SchoolRegistration(BaseModel):
    school_name: str
    syllabus_type: str
    admin_name: str
    mobile_number: str
    email: str
    password: str  # Corrected typo from 'pasword' to 'password'

sch_router = APIRouter()

@sch_router.post("/schregister")
async def register_school(school: SchoolRegistration):
    # Generate a 12-digit SCHOOL_ID with only numbers
    SCHOOL_ID = ''.join(random.choices(string.digits, k=10))
    
    # Use the password provided by the frontend
    PASSWORD = school.password

    # Ensure the mobile number includes the country code +91
    MOBILE_NUMBER = f"+91{school.mobile_number}" if not school.mobile_number.startswith("+91") else school.mobile_number

    db = get_db1()
    cursor = db.cursor()

    # Create address table without the mobile_number column
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS address (
        address_id INT PRIMARY KEY AUTO_INCREMENT,
        d_no VARCHAR(50) DEFAULT NULL,
        street VARCHAR(100) DEFAULT NULL,
        area VARCHAR(100) DEFAULT NULL,
        city VARCHAR(100) DEFAULT NULL,
        district VARCHAR(100) DEFAULT NULL,
        state VARCHAR(100) DEFAULT NULL,
        pin_code VARCHAR(10) DEFAULT NULL,
        geo_tag VARCHAR(100) DEFAULT NULL
    )
    """)

    # Create schools table with a foreign key reference to address
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schools (
        id INT PRIMARY KEY AUTO_INCREMENT,
        school_id VARCHAR(50) NOT NULL,
        school_name VARCHAR(100) DEFAULT NULL,
        syllabus_type VARCHAR(50) DEFAULT NULL,
        administrative_head_name VARCHAR(100) DEFAULT NULL,
        administrative_head_number VARCHAR(15) DEFAULT NULL,
        administrative_head_email VARCHAR(100) DEFAULT NULL,
        password VARCHAR(255) NOT NULL,
        school_logo VARCHAR(255) DEFAULT NULL,
        address_id INT DEFAULT NULL,
        token VARCHAR(255) DEFAULT NULL,
        otp VARCHAR(10) DEFAULT NULL,
        CONSTRAINT fk_address FOREIGN KEY (address_id) REFERENCES address(address_id) ON DELETE CASCADE
    )
    """)

    # Insert into schools table
    cursor.execute(
        "INSERT INTO schools (school_id, school_name, syllabus_type, administrative_head_name, administrative_head_number, administrative_head_email, password) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (SCHOOL_ID, school.school_name, school.syllabus_type, school.admin_name, MOBILE_NUMBER, school.email, PASSWORD)
    )

    # Insert into address table (optional, if address details are provided later)
    cursor.execute(
        "INSERT INTO address (d_no, street, area, city, district, state, pin_code, geo_tag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (None, None, None, None, None, None, None, None)  # Replace with actual address details if available
    )

    db.commit()

    return {"SCHOOL_ID": SCHOOL_ID, "PASSWORD": PASSWORD}