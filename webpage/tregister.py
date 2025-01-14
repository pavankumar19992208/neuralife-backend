from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
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
    characters = string.ascii_letters + string.digits
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
        Name VARCHAR(255),
        photo VARCHAR(255),
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
    check_contact_query = "SELECT Name FROM teachers WHERE contactNumber = %s"
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
        userid, SchoolId, Name, photo, dob, gender, contactNumber, email, currentAddress, permanentAddress, position,
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
    
    # Create staffallocation table if not exists
    create_staffallocation_table_query = """
    CREATE TABLE IF NOT EXISTS staffallocation (
        id INT AUTO_INCREMENT PRIMARY KEY,
        schoolid VARCHAR(255),
        subject VARCHAR(255),
        nursery JSON,
        LKG JSON,
        UKG JSON,
        class_1 JSON,
        class_2 JSON,
        class_3 JSON,
        class_4 JSON,
        class_5 JSON,
        class_6 JSON,
        class_7 JSON,
        class_8 JSON,
        class_9 JSON,
        class_10 JSON,
        class_11 JSON,
        class_12 JSON
    )
    """
    cursor.execute(create_staffallocation_table_query)
    x=[]
    y=[]
    z=[]
    for subject, classes in details.subjectSpecialization.items():
        y.append(subject)
        z.append(classes)
        for i in classes:
            x.append(i)
    x=set(x)
    print(x,y,z)

    # Insert subjects and initialize class cells with empty dict format
    for subject in x:
        print(subject, classes)
        insert_staffallocation_query = """
        INSERT INTO staffallocation (
            schoolid, subject, nursery, LKG, UKG, class_1, class_2, class_3, class_4, class_5, class_6, class_7, class_8, class_9, class_10, class_11, class_12
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Check if the subject already exists for the given SchoolId
        check_subject_query = "SELECT 1 FROM staffallocation WHERE SchoolId = %s AND subject = %s"
        cursor.execute(check_subject_query, (details.SchoolId, subject))
        existing_subject = cursor.fetchone()
        
        # Perform the insertion if the subject does not exist
        if not existing_subject:
            cursor.execute(insert_staffallocation_query, (
                details.SchoolId, subject, json.dumps({"teacherlist": [], "allocatedteacher": []}),
                json.dumps({"teacherlist": [], "allocatedteacher": []}), json.dumps({"teacherlist": [], "allocatedteacher": []}),
                json.dumps({"teacherlist": [], "allocatedteacher": []}), json.dumps({"teacherlist": [], "allocatedteacher": []}),
                json.dumps({"teacherlist": [], "allocatedteacher": []}), json.dumps({"teacherlist": [], "allocatedteacher": []}),
                json.dumps({"teacherlist": [], "allocatedteacher": []}), json.dumps({"teacherlist": [], "allocatedteacher": []}),
                json.dumps({"teacherlist": [], "allocatedteacher": []}), json.dumps({"teacherlist": [], "allocatedteacher": []}),
                json.dumps({"teacherlist": [], "allocatedteacher": []}), json.dumps({"teacherlist": [], "allocatedteacher": []}),
                json.dumps({"teacherlist": [], "allocatedteacher": []}), json.dumps({"teacherlist": [], "allocatedteacher": []}),
            ))
        
        # Continue with the remaining code
        # ...existing code...
    
    # # Update staffallocation table with teacherid in teacherlist for each class
    # for subject, classes in details.subjectSpecialization.items():
    #     for class_name in classes:
    #         update_staffallocation_query = """
    #         UPDATE staffallocation
    #         SET {class_name} = JSON_SET({class_name}, '$.teacherlist', JSON_ARRAY_APPEND(JSON_EXTRACT({class_name}, '$.teacherlist'), '$', %s))
    #         WHERE schoolid = %s AND subject = %s
    #         """
    #         cursor.execute(update_staffallocation_query.format(class_name=class_name), (userid, details.SchoolId, subject))
    # Update staffallocation table with teacherid in teacherlist for each class
    for i in range(len(y)):
        clas = y[i]
        clas = clas.replace(" ", "_")
        clas = clas.lower()
        for subject in z[i]:
            print(clas, subject)
            update_staffallocation_query = """
            UPDATE staffallocation
            SET {clas} = JSON_SET({clas}, '$.teacherlist', JSON_ARRAY_APPEND(JSON_EXTRACT({clas}, '$.teacherlist'), '$', %s))
            WHERE schoolid = %s AND subject = %s
            """
            cursor.execute(update_staffallocation_query.format(clas=clas), (userid, details.SchoolId, subject))
    
    db.commit()
    
    return {"message": f"{details.fullName} was registered successfully", "userid": userid, "password": generated_password}

@teacher_router.get("/teachers")
async def get_teachers(db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT teacherid, Name FROM teachers")
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