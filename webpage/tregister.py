from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
from pydantic import BaseModel, EmailStr
from datetime import date
import mysql.connector
from typing import List, Dict, Optional, Literal
import json
import secrets
import string
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

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
    school_id: Optional[str] = None
    name: Optional[str] = None
    profilepic: Optional[str] = None
    teacher_dob: Optional[date] = None
    gender: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[EmailStr] = None
    currentAddress: Optional[Address] = None
    permanentAddress: Optional[Address] = None
    position: Optional[List[str]] = None
    subjectSpecialization: Optional[Dict[str, List[str]]] = None
    experience: Optional[int] = None
    qualification: Optional[str] = None
    certifications: Optional[str] = None
    joining_date: Optional[date] = None
    # employment_type: Optional[str] = None
    employment_type: Optional[Literal['Permanent', 'Contract', 'Temporary']] = None
    previousSchool: Optional[str] = None
    emergencyContactName: Optional[str] = None
    emergencyContactNumber: Optional[str] = None
    relationshipToTeacher: Optional[str] = None
    languagesKnown: Optional[List[str]] = None
    interests: Optional[str] = None
    availabilityOfExtraCirricularActivities: Optional[str] = None
    documents: Optional[Documents] = None

class Documents(BaseModel):
    resume: Optional[str] = None
    photoID: Optional[str] = None
    educationalCertificates: Optional[str] = None

def generate_password(length=8):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password

@teacher_router.post("/registerteacher")
async def register_teacher(details: TeacherRegistration, db=Depends(get_db1)):
    cursor = db.cursor()

    # Normalize employment_type to match ENUM values
    if details.employment_type:
        details.employment_type = details.employment_type.capitalize()

    # Fetch the incremental school ID from the schools table
    fetch_school_id_query = "SELECT id FROM schools WHERE school_id = %s"
    cursor.execute(fetch_school_id_query, (details.school_id,))
    school = cursor.fetchone()
    
    if not school:
        raise HTTPException(status_code=404, detail=f"School with ID {details.school_id} not found")
    
    school_id = school[0]  # Get the incremental ID of the school

        
    # Check if contactNumber already exists
    check_contact_query = "SELECT Name FROM teachers WHERE contact_number = %s"
    cursor.execute(check_contact_query, (details.contact_number,))
    existing_teacher = cursor.fetchone()
    
    if existing_teacher:
        return {"message": f"{details.contact_number} is already registered with name {existing_teacher[0]}"}
    
    # Generate a password
    generated_password = generate_password()
    
    # Generate userid
    teacher_user_id = f"T{details.contact_number}"
    
    # Insert values into teachers table
    insert_teacher_query = """
    INSERT INTO teachers (
        teacher_user_id, school_id, name, teacher_dob, gender, contact_number, email, joining_date, employment_type, password
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_teacher_query, (
        teacher_user_id, school_id, details.name, details.teacher_dob, details.gender, details.contact_number, details.email,
        details.joining_date, details.employment_type, generated_password
    ))
    
    db.commit()
    
    return {"message": f"{details.name} was registered successfully", "userid": teacher_user_id, "password": generated_password}

@teacher_router.get("/teachers")
async def get_teachers(db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT teacherid, Name, qualification, experience FROM teachers")
    teachers = cursor.fetchall()
    return {"teachers": teachers}

@teacher_router.get("/teachers/{teacherid}")
async def get_teacher_details(teacherid: int, db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teachers WHERE teacherid = %s", (teacherid,))
    teacher = cursor.fetchone()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Assuming subjectSpecialization is stored as JSON in the database
    teacher['subjectSpecialization'] = json.loads(teacher['subjectSpecialization']) if teacher['subjectSpecialization'] else {}
    return teacher

@teacher_router.put("/teachers/{teacherid}/documents")
async def update_teacher_documents(teacherid: int, documents: Documents, db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT documents, Name FROM teachers WHERE teacherid = %s", (teacherid,))
    teacher = cursor.fetchone()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    existing_documents = json.loads(teacher['documents']) if teacher['documents'] else {}
        
    # Log the new documents provided
    new_documents = documents.dict(exclude_unset=True)
    logging.info(f"New documents provided: {new_documents}")
    
    # Update the existing documents with the new documents
    updated_documents = {**existing_documents, **new_documents}
    
    # Log the updated documents
    logging.info(f"Updated documents for teacher {teacher['Name']} (ID: {teacherid}): {updated_documents}")
    
    update_documents_query = "UPDATE teachers SET documents = %s WHERE teacherid = %s"
    cursor.execute(update_documents_query, (json.dumps(updated_documents), teacherid))
    db.commit()
    
    return {"message": "Documents updated successfully"}

