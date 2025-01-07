from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
import mysql.connector
import secrets
import string
from typing import List, Dict, Optional
from datetime import date
import json

studentregistration_router = APIRouter()

class StudentRegistration(BaseModel):
    SchoolId: Optional[str] = None  # Default value set to 1
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

def generate_user_id(mobile_number: str, db):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM student WHERE MobileNumber = %s", (mobile_number,))
    count = cursor.fetchone()[0]
    return f"S{mobile_number}" if count == 0 else f"S{mobile_number}{count}"

def generate_password(length=8):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password

@studentregistration_router.post("/registerstudent")
async def register_student(details: StudentRegistration, db=Depends(get_db1)):
    cursor = db.cursor()
    
    # Check if Aadhar number already exists
    cursor.execute("SELECT Name FROM student WHERE AadharNumber = %s", (details.AadharNumber,))
    existing_student = cursor.fetchone()
    if existing_student:
        student_name = existing_student[0]
        return {"message": f"Aadhar number {details.AadharNumber} already exists with {student_name}"}

    # Create table if not exists
    create_table_query = """
    CREATE TABLE IF NOT EXISTS student (
        StudentId INT AUTO_INCREMENT PRIMARY KEY,
        SchoolId INT,
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

    # Ensure SchoolId is set to 1
    # details.SchoolId = 1

    # Generate UserId
    user_id = generate_user_id(details.MobileNumber, db)

    # Generate Password
    password = generate_password()

    # Insert student details into the database
    insert_query = """
    INSERT INTO student (
        SchoolId, Name, DOB, Gender, Photo, Grade, PreviousSchool, LanguagesKnown, Religion, Category,
        MotherName, FatherName, Nationality, AadharNumber, GuardianName, MobileNumber, Email, EmergencyContact,
        CurrentAddress, PermanentAddress, PreviousPercentage,BloodGroup, MedicalDisability,
        Documents,Password, UserId, ParentOccupation, ParentQualification
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (
        details.SchoolId, details.StudentName, details.DOB, details.Gender, details.Photo, details.Grade, details.PreviousSchool,
        json.dumps(details.LanguagesKnown), details.Religion, details.Category, details.MotherName, details.FatherName,
        details.Nationality, details.AadharNumber, details.GuardianName, details.MobileNumber, details.Email, details.EmergencyContact,
        json.dumps(details.CurrentAddress), json.dumps(details.PermanentAddress), details.PreviousPercentage,
        details.BloodGroup, details.MedicalDisability, json.dumps(details.Documents),
        password, user_id, details.ParentOccupation, details.ParentQualification
    ))

    db.commit()

    return {"message": "Registered", "UserId": user_id, "Password": password}