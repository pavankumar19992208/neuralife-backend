from fastapi import APIRouter, HTTPException, Depends
from shared.db import get_db1
from pydantic import BaseModel, EmailStr
from datetime import date
import mysql.connector
from typing import List, Dict, Optional
import json
import secrets
import string

teacher_router = APIRouter()

class Address(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

class Documents(BaseModel):
    resume: Optional[str] = None
    photoID: Optional[str] = None
    educationalCertificates: Optional[str] = None

class TeacherRegistration(BaseModel):
    SchoolId: Optional[str] = None
    fullName: Optional[str] = None
    profilepic: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    contactNumber: Optional[str] = None
    email: Optional[EmailStr] = None
    currentAddress: Optional[Address] = None
    permanentAddress: Optional[Address] = None
    position: Optional[List[str]] = None
    subjectSpecialization: Optional[Dict[str, List[str]]] = None
    experience: Optional[int] = None
    qualification: Optional[str] = None
    certifications: Optional[str] = None
    joiningDate: Optional[date] = None
    employmentType: Optional[str] = None
    previousSchool: Optional[str] = None
    emergencyContactName: Optional[str] = None
    emergencyContactNumber: Optional[str] = None
    relationshipToTeacher: Optional[str] = None
    languagesKnown: Optional[List[str]] = None
    interests: Optional[str] = None
    availabilityOfExtraCirricularActivities: Optional[str] = None
    documents: Optional[Documents] = None

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
        userid VARCHAR(255),
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
    # Check if contactNumber already exists
    check_contact_query = "SELECT fullName FROM teachers WHERE contactNumber = %s"
    cursor.execute(check_contact_query, (details.contactNumber,))
    existing_teacher = cursor.fetchone()
    
    if existing_teacher:
        return {"message": f"{details.contactNumber} is already registered with name {existing_teacher[0]}"}
    

    
    # Generate a password
    generated_password = generate_password()
    
    # Generate userid
    userid = f"T{details.contactNumber}"
    
    # Insert values into teachers table
    insert_teacher_query = """
    INSERT INTO teachers (
        userid, SchoolId, fullName, profilepic, dob, gender, contactNumber, email, currentAddress, permanentAddress, position,
        subjectSpecialization, experience, qualification, certifications, joiningDate, employmentType, previousSchool, emergencyContactName, emergencyContactNumber, relationshipToTeacher,
        languagesKnown, interests, availabilityOfExtraCirricularActivities, documents, password
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_teacher_query, (
        userid, details.SchoolId, details.fullName, details.profilepic, details.dob, details.gender, details.contactNumber, details.email,
        json.dumps(details.currentAddress.dict()) if details.currentAddress else None,
        json.dumps(details.permanentAddress.dict()) if details.permanentAddress else None,
        json.dumps(details.position) if details.position else None,
        json.dumps(details.subjectSpecialization) if details.subjectSpecialization else None,
        details.experience, details.qualification, details.certifications, details.joiningDate, details.employmentType, details.previousSchool, details.emergencyContactName, details.emergencyContactNumber,
        details.relationshipToTeacher, json.dumps(details.languagesKnown) if details.languagesKnown else None,
        details.interests, details.availabilityOfExtraCirricularActivities,
        json.dumps(details.documents.dict()) if details.documents else None, generated_password
    ))
    
    db.commit()
    
    return {"message": f"{details.fullName} was registered successfully", "userid": userid, "password": generated_password}