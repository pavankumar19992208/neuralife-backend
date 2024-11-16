from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
from pydantic import BaseModel
import mysql.connector
from typing import List, Dict
import json

teacher_router = APIRouter()

class TeacherRegistration(BaseModel):
    SchoolId: str
    fullName: str
    profilepic: str
    dob: str
    gender: str
    contactNumber: str
    email: str
    currentAddress: Dict[str, str]
    permanentAddress: Dict[str, str]
    position: str
    subjectSpecialization: List[str]
    grade: str
    experience: str
    qualification: str
    certifications: str
    joiningDate: str
    employmentType: str
    otherEmploymentType: str
    previousSchool: str
    emergencyContactName: str
    emergencyContactNumber: str
    relationshipToTeacher: str
    languagesKnown: List[str]
    interests: str
    availabilityOfExtraCirricularActivities: bool
    documents: Dict[str, str]

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
        position VARCHAR(255),
        subjectSpecialization JSON,
        grade VARCHAR(50),
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
        availabilityOfExtraCirricularActivities BOOLEAN,
        documents JSON
    )
    """
    cursor.execute(create_teachers_table_query)
    
    # Insert values into teachers table
    insert_teacher_query = """
    INSERT INTO teachers (
        SchoolId, fullName, profilepic, dob, gender, contactNumber, email, currentAddress, permanentAddress, position,
        subjectSpecialization, grade, experience, qualification, certifications, joiningDate, employmentType,
        otherEmploymentType, previousSchool, emergencyContactName, emergencyContactNumber, relationshipToTeacher,
        languagesKnown, interests, availabilityOfExtraCirricularActivities, documents
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_teacher_query, (
        details.SchoolId, details.fullName, details.profilepic, details.dob, details.gender, details.contactNumber, details.email,
        json.dumps(details.currentAddress), json.dumps(details.permanentAddress), details.position,
        json.dumps(details.subjectSpecialization), details.grade, details.experience, details.qualification,
        details.certifications, details.joiningDate, details.employmentType, details.otherEmploymentType,
        details.previousSchool, details.emergencyContactName, details.emergencyContactNumber,
        details.relationshipToTeacher, json.dumps(details.languagesKnown), details.interests,
        details.availabilityOfExtraCirricularActivities, json.dumps(details.documents)
    ))
    
    db.commit()
    
    return {"message": f"{details.fullName} was registered successfully"}