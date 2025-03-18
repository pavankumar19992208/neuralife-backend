from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException, Depends, Path
from db import get_db1
import mysql.connector
import secrets
import string
from typing import List, Dict, Optional, Union
from datetime import date
import json
import logging
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

studentregistration_router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)

sns_client = boto3.client(
    "sns",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="eu-north-1"
)

class StudentRegistration(BaseModel):
    SchoolId: Optional[str] = None
    StudentName: Optional[str] = None
    DOB: Optional[date] = None
    Gender: Optional[str] = None  # Changed to str for compatibility with varchar(10)
    Photo: Optional[str] = None
    Grade: Optional[int] = None
    PreviousSchool: Optional[str] = None
    LanguagesKnown: Optional[List[str]] = None
    Religion: Optional[str] = None
    Category: Optional[str] = None
    MotherName: Optional[str] = None
    FatherName: Optional[str] = None
    Nationality: Optional[str] = None
    AadharNumber: Optional[str] = None
    GuardianName: Optional[str] = None
    MobileNumber: Optional[str] = None
    Email: Optional[EmailStr] = None
    EmergencyContact: Optional[str] = None
    CurrentAddress: Optional[Dict[str, str]] = None
    PermanentAddress: Optional[Dict[str, str]] = None
    PreviousPercentage: Optional[float] = None
    BloodGroup: Optional[str] = None
    MedicalDisability: Optional[str] = None
    Documents: Optional[Dict[str, str]] = None
    ParentOccupation: Optional[str] = None
    ParentQualification: Optional[str] = None

class DocumentUploadPayload(BaseModel):
    Documents: Dict[str, str]

def generate_user_id(mobile_number: str, db):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM student WHERE MobileNumber = %s", (mobile_number,))
    count = cursor.fetchone()[0]
    return f"S{mobile_number[-10:]}" if count == 0 else f"S{mobile_number[-10:]}{count}"

def generate_password(length=8):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password

def send_sms(mobile_number: str, user_id: str, password: str, student_name: str):
    message = f"Dear {student_name}, Welcome to neuraLife Edtech, Your registration is successful. User ID: {user_id}, Password: {password}"
    try:
        response = sns_client.publish(
            PhoneNumber=mobile_number,
            Message=message
        )
        logging.info(f"SMS sent successfully. Response: {response}")
    except Exception as e:
        logging.error(f"Failed to send SMS. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send SMS. Error: {e}")


@studentregistration_router.post("/registerstudent")
async def register_student(details: Union[StudentRegistration, List[StudentRegistration]], db=Depends(get_db1)):
    cursor = db.cursor()

    # Create table if not exists
    create_table_query = """
    CREATE TABLE IF NOT EXISTS student (
        StudentId INT AUTO_INCREMENT PRIMARY KEY,
        SchoolId VARCHAR(50),
        Name VARCHAR(255),
        DOB DATE,
        Gender VARCHAR(10),
        Photo VARCHAR(255),
        Grade INT,
        PreviousSchool VARCHAR(255),
        LanguagesKnown JSON,
        Religion VARCHAR(50),
        Category VARCHAR(50),
        MotherName VARCHAR(255),
        FatherName VARCHAR(255),
        Nationality VARCHAR(50),
        AadharNumber VARCHAR(20) UNIQUE,
        GuardianName VARCHAR(255),
        MobileNumber VARCHAR(15),
        Email VARCHAR(255),
        EmergencyContact VARCHAR(15),
        CurrentAddress JSON,
        PermanentAddress JSON,
        PreviousPercentage FLOAT,
        BloodGroup VARCHAR(10),
        MedicalDisability VARCHAR(255),
        Documents JSON,
        Password VARCHAR(255),
        UserId VARCHAR(255),
        ParentOccupation VARCHAR(255),
        ParentQualification VARCHAR(255)
    )
    """
    cursor.execute(create_table_query)

    if isinstance(details, StudentRegistration):
        details = [details]

    for detail in details:
        # Check if Aadhar number already exists
        cursor.execute("SELECT Name FROM student WHERE AadharNumber = %s", (detail.AadharNumber,))
        existing_student = cursor.fetchone()
        if existing_student:
            student_name = existing_student[0]
            logging.info(f"Aadhar number {detail.AadharNumber} already exists with {student_name}")
            raise HTTPException(status_code=409, detail=f"Aadhar number {detail.AadharNumber} already exists with {student_name}")

        # Prepend +91 to MobileNumber
        mobile_number_with_country_code = f"+91{detail.MobileNumber}"

        # Generate UserId
        user_id = generate_user_id(mobile_number_with_country_code, db)

        # Generate Password
        password = generate_password()

        # Insert student details into the database
        insert_query = """
        INSERT INTO student (
            SchoolId, Name, DOB, Gender, Photo, Grade, PreviousSchool, LanguagesKnown, Religion, Category,
            MotherName, FatherName, Nationality, AadharNumber, GuardianName, MobileNumber, Email, EmergencyContact,
            CurrentAddress, PermanentAddress, PreviousPercentage, BloodGroup, MedicalDisability,
            Documents, Password, UserId, ParentOccupation, ParentQualification
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            detail.SchoolId, detail.StudentName, detail.DOB, detail.Gender, detail.Photo, detail.Grade, detail.PreviousSchool,
            json.dumps(detail.LanguagesKnown), detail.Religion, detail.Category, detail.MotherName, detail.FatherName,
            detail.Nationality, detail.AadharNumber, detail.GuardianName, mobile_number_with_country_code, detail.Email, detail.EmergencyContact,
            json.dumps(detail.CurrentAddress), json.dumps(detail.PermanentAddress), detail.PreviousPercentage,
            detail.BloodGroup, detail.MedicalDisability, json.dumps(detail.Documents),
            password, user_id, detail.ParentOccupation, detail.ParentQualification
        ))

        # Send SMS with user ID and password
        send_sms(mobile_number_with_country_code, user_id, password, detail.StudentName)

    db.commit()

    return {"message": "Registered", "UserId": user_id, "Password": password}

@studentregistration_router.get("/grades")
async def get_grades(db=Depends(get_db1)):
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT Grade FROM student ORDER BY Grade")
    grades = cursor.fetchall()
    return {"grades": [grade[0] for grade in grades]}

@studentregistration_router.get("/students/{grade}")
async def get_students_by_grade(grade: int, db=Depends(get_db1)):
    cursor = db.cursor()
    cursor.execute("SELECT StudentId, Name, Grade FROM student WHERE Grade = %s", (grade,))
    students = cursor.fetchall()
    return {"students": [{"StudentId": student[0], "Name": student[1], "Grade": student[2]} for student in students]}

@studentregistration_router.get("/student/{StudentId}")
async def get_student_by_id(StudentId: int, db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM student WHERE StudentId = %s", (StudentId,))
    student = cursor.fetchone()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"student": student}

@studentregistration_router.post("/uploaddocuments/{student_id}")
async def upload_documents(student_id: int, payload: DocumentUploadPayload, db=Depends(get_db1)):
    logging.info(f"Received documents payload: {payload.Documents}")

    cursor = db.cursor()

    # Check if the student exists
    cursor.execute("SELECT Documents FROM student WHERE StudentId = %s", (student_id,))
    student = cursor.fetchone()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing_documents = json.loads(student[0]) if student[0] else {}

    # Update the documents for the existing student
    updated_documents = {**existing_documents, **payload.Documents}
    update_query = """
    UPDATE student
    SET Documents = %s
    WHERE StudentId = %s
    """
    cursor.execute(update_query, (json.dumps(updated_documents), student_id))

    db.commit()

    return {"message": "Documents uploaded successfully"}