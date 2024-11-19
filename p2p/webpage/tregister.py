from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
from pydantic import BaseModel
from datetime import date
import mysql.connector
from typing import List, Dict
import json
import secrets
import string

teacher_router = APIRouter()

class Address(BaseModel):
    line1: str
    line2: str
    city: str
    district: str
    state: str
    pincode: str

class Documents(BaseModel):
    resume: str
    photoID: str
    educationalCertificates: str

class TeacherRegistration(BaseModel):
    SchoolId: str
    fullName: str
    profilepic: str
    dob: date
    gender: str
    contactNumber: str
    email: str
    currentAddress: Address
    permanentAddress: Address
    position: List[str]
    subjectSpecialization: Dict[str, List[str]]
    experience: int
    qualification: str
    certifications: str
    joiningDate: date
    employmentType: str
    otherEmploymentType: str = None
    previousSchool: str
    emergencyContactName: str
    emergencyContactNumber: str
    relationshipToTeacher: str
    languagesKnown: List[str]
    interests: str
    availabilityOfExtraCirricularActivities: str
    documents: Documents

def generate_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password

@teacher_router.post("/registerteacher")
async def register_teacher(details: TeacherRegistration, db=Depends(get_db1)):
    cursor = db.cursor()
    
    # Create teachers table if not exists
    create_teachers_table_query = """
    CREATE TABLE IF NOT EXISTS teachers (
        teacherid INT AUTO_INCREMENT PRIMARY KEY,
        SchoolId VARCHAR(255),
        fullName VARCHAR(255),
        profilepic VARCHAR(255),
        dob DATE,
        gender VARCHAR(10),
        contactNumber VARCHAR(20),
        email VARCHAR(255),
        currentAddress JSON,
        permanentAddress JSON,
        position JSON,
        subjectSpecialization JSON,
        experience INT,
        qualification VARCHAR(255),
        certifications TEXT,
        joiningDate DATE,
        employmentType VARCHAR(50),
        otherEmploymentType VARCHAR(50),
        previousSchool VARCHAR(255),
        emergencyContactName VARCHAR(255),
        emergencyContactNumber VARCHAR(20),
        relationshipToTeacher VARCHAR(50),
        languagesKnown JSON,
        interests TEXT,
        availabilityOfExtraCirricularActivities VARCHAR(255),
        documents JSON,
        password VARCHAR(255)
    )
    """
    cursor.execute(create_teachers_table_query)
    
    # Generate a password
    generated_password = generate_password()
    
    # Insert values into teachers table
    insert_teacher_query = """
    INSERT INTO teachers (
        SchoolId, fullName, profilepic, dob, gender, contactNumber, email, currentAddress, permanentAddress, position,
        subjectSpecialization,experience, qualification, certifications, joiningDate, employmentType,
        otherEmploymentType, previousSchool, emergencyContactName, emergencyContactNumber, relationshipToTeacher,
        languagesKnown, interests, availabilityOfExtraCirricularActivities, documents, password
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_teacher_query, (
        details.SchoolId, details.fullName, details.profilepic, details.dob, details.gender, details.contactNumber, details.email,
        json.dumps(details.currentAddress.dict()), json.dumps(details.permanentAddress.dict()), json.dumps(details.position),
        json.dumps(details.subjectSpecialization),details.experience, details.qualification,
        details.certifications, details.joiningDate, details.employmentType, details.otherEmploymentType,
        details.previousSchool, details.emergencyContactName, details.emergencyContactNumber,
        details.relationshipToTeacher, json.dumps(details.languagesKnown), details.interests,
        details.availabilityOfExtraCirricularActivities, json.dumps(details.documents.dict()), generated_password
    ))
    
    db.commit()
    
    return {"message": f"{details.fullName} was registered successfully", "password": generated_password}