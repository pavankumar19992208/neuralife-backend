from fastapi import APIRouter, HTTPException
from db import get_db1
from pydantic import BaseModel
import random
import string
import mysql.connector
import boto3
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

class SchoolRegistration(BaseModel):
    school_name: str
    syllabus_type: str
    admin_name: str
    mobile_number: str
    email: str
    password: str

class LoginRequest(BaseModel):
    schoolId: str = None
    mobile_number: str = None
    password: str

class SendOTPRequest(BaseModel):
    mobile_number: str

sch_router = APIRouter()

@sch_router.post("/schregister")
async def register_school(school: SchoolRegistration):
    SCHOOL_ID = ''.join(random.choices(string.digits, k=10))
    PASSWORD = school.password
    MOBILE_NUMBER = f"+91{school.mobile_number}" if not school.mobile_number.startswith("+91") else school.mobile_number

    db = get_db1()
    cursor = db.cursor()

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

    cursor.execute(
        "INSERT INTO schools (school_id, school_name, syllabus_type, administrative_head_name, administrative_head_number, administrative_head_email, password) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (SCHOOL_ID, school.school_name, school.syllabus_type, school.admin_name, MOBILE_NUMBER, school.email, PASSWORD)
    )

    cursor.execute(
        "INSERT INTO address (d_no, street, area, city, district, state, pin_code, geo_tag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (None, None, None, None, None, None, None, None)
    )

    db.commit()

    return {"SCHOOL_ID": SCHOOL_ID, "PASSWORD": PASSWORD}

@sch_router.post("/login")
async def login(login_request: LoginRequest):
    db = get_db1()
    cursor = db.cursor(dictionary=True)

    if login_request.schoolId:
        cursor.execute(
            "SELECT * FROM schools WHERE school_id = %s AND password = %s",
            (login_request.schoolId, login_request.password)
        )
    elif login_request.mobile_number:
        MOBILE_NUMBER = f"+91{login_request.mobile_number}" if not login_request.mobile_number.startswith("+91") else login_request.mobile_number
        cursor.execute(
            "SELECT * FROM schools WHERE administrative_head_number = %s AND password = %s",
            (MOBILE_NUMBER, login_request.password)
        )
    else:
        raise HTTPException(status_code=400, detail="Either schoolId or mobile_number must be provided")

    school = cursor.fetchone()

    if not school:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful", "school": school}

@sch_router.post("/send-otp")
async def send_otp(otp_request: SendOTPRequest):
    try:
        # Generate a random 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=4))
        logging.debug(f"Generated OTP: {otp}")

        # Send OTP via AWS SNS
        client = boto3.client(
            'sns',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name="eu-north-1"
        )
        logging.debug("AWS SNS client initialized")

        response = client.publish(
            PhoneNumber=otp_request.mobile_number,
            Message=f'Your OTP is {otp}'
        )
        logging.debug(f"AWS SNS response: {response}")

        # Save OTP to the database (optional)
        db = get_db1()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE schools SET otp = %s WHERE administrative_head_number = %s",
            (otp, otp_request.mobile_number)
        )
        db.commit()
        logging.debug("OTP saved to database")

        return {"message": "OTP sent successfully"}
    except Exception as e:
        logging.error(f"Error sending OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))