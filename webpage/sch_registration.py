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

# Update your SendOTPRequest model
class SendOTPRequest(BaseModel):
    mobile_number: str = None
    schoolId: str = None

class VerifyOTPRequest(BaseModel):
    mobile_number: str = None
    schoolId: str = None
    otp: str

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
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = db.cursor(dictionary=True)

    logging.debug(f"Login request: schoolId={login_request.schoolId}, mobile_number={login_request.mobile_number}, password={login_request.password}")

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
        logging.debug("Invalid credentials: No matching record found")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logging.debug(f"Login successful for school: {school}")
    return {"message": "Login successful", "school": school}

# Update the send-otp endpoint
@sch_router.post("/send-otp")
async def send_otp(otp_request: SendOTPRequest):
    try:
        db = get_db1()
        if db is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = db.cursor(dictionary=True)
        
        # Find the mobile number either directly or via school ID
        if otp_request.mobile_number:
            mobile_number = f"+91{otp_request.mobile_number}" if not otp_request.mobile_number.startswith("+91") else otp_request.mobile_number
            cursor.execute(
                "SELECT school_id, administrative_head_number FROM schools WHERE administrative_head_number = %s",
                (mobile_number,)
            )
        elif otp_request.schoolId:
            cursor.execute(
                "SELECT school_id, administrative_head_number FROM schools WHERE school_id = %s",
                (otp_request.schoolId,)
            )
        else:
            raise HTTPException(status_code=400, detail="Either mobile_number or schoolId must be provided")
        
        school = cursor.fetchone()
        if not school:
            raise HTTPException(status_code=404, detail="School not found")
        
        mobile_number = school['administrative_head_number']
        school_id = school['school_id']
        
        # Generate a random 4-digit OTP
        otp = ''.join(random.choices(string.digits, k=4))
        logging.debug(f"Generated OTP: {otp} for mobile_number: {mobile_number}, school_id: {school_id}")

        # Send OTP via AWS SNS
        client = boto3.client(
            'sns',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        
        response = client.publish(
            PhoneNumber=mobile_number,
            Message=f'Your OTP is {otp}'
        )
        logging.debug(f"AWS SNS response: {response}")

        # Store the OTP in the database for the respective school ID
        cursor.execute(
            "UPDATE schools SET otp = %s WHERE school_id = %s",
            (otp, school_id)
        )
        db.commit()
        logging.debug(f"OTP stored in database for school_id: {school_id}, mobile_number: {mobile_number}, OTP: {otp}")
        logging.debug(f"Attempting to send to: {mobile_number}")
        logging.debug(f"Full AWS credentials: {os.getenv('AWS_ACCESS_KEY_ID')[:5]}...{os.getenv('AWS_SECRET_ACCESS_KEY')[:5]}...")
        logging.debug(f"AWS Region: {os.getenv('AWS_REGION')}")

        return {"message": "OTP sent successfully", "mobile_number": mobile_number}
    except Exception as e:
        logging.error(f"Error sending OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@sch_router.post("/verify-otp-login")
async def verify_otp_login(verify_request: VerifyOTPRequest):
    db = get_db1()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = db.cursor(dictionary=True)

    # Find the school by either mobile number or school ID
    if verify_request.mobile_number:
        mobile_number = f"+91{verify_request.mobile_number}" if not verify_request.mobile_number.startswith("+91") else verify_request.mobile_number
        cursor.execute(
            "SELECT * FROM schools WHERE administrative_head_number = %s",
            (mobile_number,))
    elif verify_request.schoolId:
        cursor.execute(
            "SELECT * FROM schools WHERE school_id = %s",
            (verify_request.schoolId,))
    else:
        raise HTTPException(status_code=400, detail="Either mobile_number or schoolId must be provided")

    school = cursor.fetchone()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    # Verify OTP
    if school['otp'] != verify_request.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    # Clear the OTP after successful verification
    cursor.execute(
        "UPDATE schools SET otp = NULL WHERE school_id = %s",
        (school['school_id'],))
    db.commit()

    return {"message": "Login successful", "school": school}