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
from typing import Literal 
from dotenv import load_dotenv

load_dotenv()

studentregistration_router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)

sns_client = boto3.client(
    "sns",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="ap-south-1"
)

class Address(BaseModel):
    line1: str
    line2: Optional[str] = None
    landmark: Optional[str] = None
    locality: Optional[str] = None
    city: str
    district: str
    state: str
    country: str = "India"
    pincode: str
    address_type: str

class Occupation(BaseModel):
    occupation_id: int
    occupation_name: str
    category: str
    income_level: Optional[str] = None  # Make income_level optional

class Qualification(BaseModel):
    qualification_id: int
    qualification_name: str
    level: str
    typical_duration: Optional[str] = None
    is_technical: Optional[bool] = None
    indian_equivalent: Optional[str] = None

class StudentLanguage(BaseModel):
    language_id: int
    language_type: str  # 'mother_tongue' or 'secondary_language'

class StudentRegistration(BaseModel):
    school_id: Optional[str] = None
    name: Optional[str] = None
    dob: Optional[date] = None
    aadhar_number: Optional[str] = None
    contact_number: Optional[str] = None
    grade: Optional[int] = None
    gender: Optional[str] = None 
    student_email: Optional[str] = None
    previous_school: Optional[str] = None
    mother_name: Optional[str] = None
    father_name: Optional[str] = None
    guardian_name: Optional[str] = None
    emergency_contact: Optional[str] = None
    previous_percentage: Optional[float] = None
    religion_id: Optional[int] = None
    category_id: Optional[int] = None 
    nationality_id: Optional[int] = None
    medical_disability_id: Optional[int] = None
    parent_qualification_id: Optional[int] = None  
    parent_occupation_id: Optional[int] = None
    languages: Optional[List[StudentLanguage]] = None
    address: Optional[Address] = None


class DocumentUploadPayload(BaseModel):
    Documents: Dict[str, str]

class Disability(BaseModel):
    disability_id: int
    disability_code: str
    disability_name: str
    category: str
    description: Optional[str] = None
    requires_assistance: Optional[bool] = None
    is_rare: Optional[bool] = None

def generate_user_id(contact_number: str, db):
    if contact_number.startswith("+91"):
        contact_number = contact_number[3:]

    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM student WHERE contact_number = %s", (contact_number,))
    count = cursor.fetchone()[0]
    return f"S{contact_number[-10:]}" if count == 0 else f"S{contact_number[-10:]}{count}"

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
    
def insert_address(address_data: dict, db):
    cursor = db.cursor(dictionary=True)
    try:
        insert_query = """
        INSERT INTO addresses (
            address_line1, address_line2, landmark, locality, 
            city, district, state, country, pincode, address_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            address_data.get('line1'),
            address_data.get('line2'),
            address_data.get('landmark'),
            address_data.get('locality'),
            address_data.get('city'),
            address_data.get('district'),
            address_data.get('state'),
            address_data.get('country'),
            address_data.get('pincode'),
            address_data.get('address_type')
        ))
        address_id = cursor.lastrowid
        db.commit()
        return address_id
    except mysql.connector.Error as err:
        db.rollback()
        logging.error(f"Error inserting address: {err}")
        raise
    finally:
        cursor.close()


@studentregistration_router.post("/registerstudent")
async def register_student(details: Union[StudentRegistration, List[StudentRegistration]], db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)

    try:
        db.start_transaction()

        if isinstance(details, StudentRegistration):
            details = [details]

        results = []
        
        for detail in details:
            # Check if Aadhar number already exists
            cursor.execute("SELECT student_user_id, name FROM student WHERE aadhar_number = %s", (detail.aadhar_number,))
            existing_student = cursor.fetchone()
            if existing_student:
                results.append({
                    "student_id": None,
                    "user_id": existing_student["student_user_id"],
                    "password": None,
                    "message": f"Student with Aadhar number {detail.aadhar_number} already exists: {existing_student['name']}"
                })
                continue

            if not detail.contact_number.startswith("+91"):
                detail.contact_number = f"+91{detail.contact_number}"

            user_id = generate_user_id(detail.contact_number, db)
            password = generate_password()

            # Insert address first - convert Pydantic model to dict
            address_id = None
            if detail.address:
                address_dict = detail.address.dict()  # Convert Pydantic model to dictionary
                address_id = insert_address(address_dict, db)

            # Insert student details
            insert_query = """
            INSERT INTO student (
                school_id, name, dob, aadhar_number, contact_number, grade, gender, 
                student_email, previous_school, mother_name, father_name, guardian_name, 
                emergency_contact, previous_percentage, religion_id, category_id, 
                nationality_id, medical_disability_id, parent_qualification_id, 
                parent_occupation_id, student_user_id, password, address_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                detail.school_id, detail.name, detail.dob, detail.aadhar_number, 
                detail.contact_number, detail.grade, detail.gender, detail.student_email, 
                detail.previous_school, detail.mother_name, detail.father_name,
                detail.guardian_name, detail.emergency_contact, detail.previous_percentage, 
                detail.religion_id, detail.category_id, detail.nationality_id, 
                detail.medical_disability_id, detail.parent_qualification_id, 
                detail.parent_occupation_id, user_id, password, address_id
            ))
            student_id = cursor.lastrowid

            if detail.languages:
                mother_tongues = [lang for lang in detail.languages if lang.language_type == 'mother_tongue']
                if len(mother_tongues) > 1:
                    raise HTTPException(
                        status_code=400,
                        detail="Only one language can be marked as mother tongue"
                    )

                for lang in detail.languages:
                    cursor.execute(
                        "INSERT INTO student_languages (student_id, language_id, language_type) VALUES (%s, %s, %s)",
                        (student_id, lang.language_id, lang.language_type)
                    )

            send_sms(detail.contact_number, user_id, password, detail.name)

            results.append({
                "student_id": student_id,
                "user_id": user_id,
                "password": password,
                "message": "Student registered successfully"
            })

        db.commit()
        return results[0] if len(results) == 1 else {"registrations": results}

    except mysql.connector.Error as err:
        db.rollback()
        logging.error(f"Database error: {err}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    finally:
        cursor.close()
        
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

@studentregistration_router.get("/languages")
async def get_languages(db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT language_id, language_name FROM languages")
    languages = cursor.fetchall()
    return {"languages": languages}

# Add new endpoint for student languages
@studentregistration_router.post("/student/{student_id}/languages")
async def add_student_language(
    student_id: int = Path(..., title="The ID of the student"),
    language: StudentLanguage = ...,
    db=Depends(get_db1)
):
    cursor = db.cursor()
    try:
        # Check if student exists
        cursor.execute("SELECT student_id FROM student WHERE student_id = %s", (student_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Student not found")

        # Check if language exists
        cursor.execute("SELECT language_id FROM languages WHERE language_id = %s", (language.language_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Invalid language ID")

        # Validate only one mother tongue
        if language.language_type == 'mother_tongue':
            cursor.execute("""
                SELECT id FROM student_languages 
                WHERE student_id = %s AND language_type = 'mother_tongue'
            """, (student_id,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="Student already has a mother tongue language"
                )

        # Check if this language already exists for student
        cursor.execute("""
            SELECT id FROM student_languages 
            WHERE student_id = %s AND language_id = %s
        """, (student_id, language.language_id))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="This language is already registered for the student"
            )

        # Insert new language
        cursor.execute("""
            INSERT INTO student_languages (student_id, language_id, language_type)
            VALUES (%s, %s, %s)
        """, (student_id, language.language_id, language.language_type))

        db.commit()
        return {"message": "Language added successfully"}
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()

# Add endpoint to get student languages
@studentregistration_router.get("/student/{student_id}/languages")
async def get_student_languages(
    student_id: int = Path(..., title="The ID of the student"),
    db=Depends(get_db1)
):
    cursor = db.cursor(dictionary=True)
    try:
        # First check if student exists
        cursor.execute("SELECT student_id FROM student WHERE student_id = %s", (student_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Student not found")

        # Get student languages with language details
        cursor.execute("""
            SELECT 
                sl.id,
                l.language_id,
                l.language_name,
                sl.language_type,
                sl.created_at
            FROM student_languages sl
            JOIN languages l ON sl.language_id = l.language_id
            WHERE sl.student_id = %s
            ORDER BY 
                CASE WHEN sl.language_type = 'mother_tongue' THEN 0 ELSE 1 END,
                l.language_name
        """, (student_id,))
        
        languages = cursor.fetchall()
        return {"student_id": student_id, "languages": languages}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()

@studentregistration_router.get("/nationalities")
async def get_nationalities(db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT nationality_id, nationality_name FROM nationalities ORDER BY nationality_name")
    nationalities = cursor.fetchall()
    return {"nationalities": nationalities}

@studentregistration_router.get("/religions")
async def get_religions(db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT religion_id, religion_name FROM religions ORDER BY religion_name")
    religions = cursor.fetchall()
    return {"religions": religions}

@studentregistration_router.get("/occupations", response_model=List[Occupation])
async def get_occupations(db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            occupation_id, 
            occupation_name, 
            category, 
            COALESCE(income_level, '') as income_level  # Convert NULL to empty string
        FROM occupations
    """)
    occupations = cursor.fetchall()
    return occupations

@studentregistration_router.get("/qualifications", response_model=List[Qualification])
async def get_qualifications(db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            qualification_id, 
            qualification_name, 
            level, 
            typical_duration,
            is_technical,
            indian_equivalent
        FROM qualifications
        ORDER BY qualification_name
    """)
    qualifications = cursor.fetchall()
    return qualifications

@studentregistration_router.get("/disabilities", response_model=List[Disability])
async def get_disabilities(db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            disability_id, 
            disability_code, 
            disability_name, 
            category,
            description,
            requires_assistance,
            is_rare
        FROM disabilities
        ORDER BY disability_name
    """)
    return cursor.fetchall()

@studentregistration_router.get("/categories")
async def get_categories(db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            category_id, 
            category_code, 
            category_name,
            category_type
        FROM reservation_categories
        ORDER BY category_name
    """)
    categories = cursor.fetchall()
    return {"categories": categories}