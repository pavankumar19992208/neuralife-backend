from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
from pydantic import BaseModel
import mysql.connector
from typing import List, Dict, Optional
import json
import logging

school_data = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchoolInternalData(BaseModel):
    SchoolId: str
    State: str
    SchoolType: str
    Curriculum: str
    OtherCurriculum: str
    GradeLevelFrom: str
    GradeLevelTo: str
    Subjects: List[str]
    Medium: str
    AcademicYearStart: str  # Format: YYYY-MM
    AcademicYearEnd: str    # Format: YYYY-MM
    ExtraPrograms: List[str]
    SchoolTimingFrom: str
    SchoolTimingTo: str
    ExamPattern: str
    OtherExamPattern: str
    AssessmentCriteria: str
    OtherAssessmentCriteria: str
    FeeStructure: List[Dict[str, str]]
    TotalAmount: float
    TeachingStaff: List[str]
    NonTeachingStaff: List[str]
    GradesOffered: List[str]

class SchoolIdRequest(BaseModel):
    SchoolId: str

class TeacherRequest(BaseModel):
    SchoolId: str
    Class: str
    Subject: Optional[str] = None

class AllottedTeachersRequest(BaseModel):
    SchoolId: str
    AllottedTeachers: Dict[str, Dict[str, str]]

@school_data.post("/schooldata")
async def create_school_internal_data(details: SchoolInternalData, db=Depends(get_db1)):
    cursor = db.cursor()
    
    # Create schooldata table if not exists
    create_schooldata_table_query = """
    CREATE TABLE IF NOT EXISTS schooldata (
        id INT AUTO_INCREMENT PRIMARY KEY,
        SchoolId VARCHAR(255),
        State VARCHAR(255),
        SchoolType VARCHAR(255),
        Curriculum VARCHAR(255),
        OtherCurriculum VARCHAR(255),
        GradeLevelFrom VARCHAR(255),
        GradeLevelTo VARCHAR(255),
        Subjects JSON,
        Medium VARCHAR(255),
        AcademicYearStart VARCHAR(10),  # Format: YYYY-MM
        AcademicYearEnd VARCHAR(10),    # Format: YYYY-MM
        ExtraPrograms JSON,
        SchoolTimingFrom TIME,
        SchoolTimingTo TIME,
        ExamPattern VARCHAR(255),
        OtherExamPattern VARCHAR(255),
        AssessmentCriteria VARCHAR(255),
        OtherAssessmentCriteria VARCHAR(255),
        FeeStructure JSON,
        TotalAmount FLOAT,
        TeachingStaff JSON,
        NonTeachingStaff JSON,
        GradesOffered JSON
    )
    """
    cursor.execute(create_schooldata_table_query)

    # Check if GradesOffered column exists
    cursor.execute("SHOW COLUMNS FROM schooldata LIKE 'GradesOffered'")
    result = cursor.fetchone()
    if not result:
        # Alter table to add GradesOffered column if it does not exist
        alter_table_query = """
        ALTER TABLE schooldata 
        ADD COLUMN GradesOffered JSON
        """
        cursor.execute(alter_table_query)
    
    # Insert values into schooldata table
    insert_schooldata_query = """
    INSERT INTO schooldata (
        SchoolId, State, SchoolType, Curriculum, OtherCurriculum, GradeLevelFrom, GradeLevelTo, Subjects, Medium,
        AcademicYearStart, AcademicYearEnd, ExtraPrograms, SchoolTimingFrom, SchoolTimingTo, ExamPattern,
        OtherExamPattern, AssessmentCriteria, OtherAssessmentCriteria, FeeStructure, TotalAmount, TeachingStaff, NonTeachingStaff, GradesOffered
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_schooldata_query, (
        details.SchoolId, details.State, details.SchoolType, details.Curriculum, details.OtherCurriculum,
        details.GradeLevelFrom, details.GradeLevelTo, json.dumps(details.Subjects), details.Medium,
        details.AcademicYearStart, details.AcademicYearEnd, json.dumps(details.ExtraPrograms),
        details.SchoolTimingFrom, details.SchoolTimingTo, details.ExamPattern, details.OtherExamPattern,
        details.AssessmentCriteria, details.OtherAssessmentCriteria, json.dumps(details.FeeStructure),
        details.TotalAmount, json.dumps(details.TeachingStaff), json.dumps(details.NonTeachingStaff), json.dumps(details.GradesOffered)
    ))
    
    db.commit()
    
    return {"message": "Details updated successfully"}

@school_data.post("/schoolinfo")
async def get_school_info(school_id_request: SchoolIdRequest, db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Query to get the row that matches the given SchoolId
    get_schooldata_query = "SELECT * FROM schooldata WHERE SchoolId = %s"
    cursor.execute(get_schooldata_query, (school_id_request.SchoolId,))
    
    # Fetch the row
    row = cursor.fetchone()
    
    if row:
        # Convert JSON fields back to Python objects
        row['Subjects'] = json.loads(row['Subjects'])
        row['ExtraPrograms'] = json.loads(row['ExtraPrograms'])
        row['FeeStructure'] = json.loads(row['FeeStructure'])
        row['TeachingStaff'] = json.loads(row['TeachingStaff'])
        row['NonTeachingStaff'] = json.loads(row['NonTeachingStaff'])
        row['GradesOffered'] = json.loads(row['GradesOffered'])  # Ensure GradesOffered is included
        return {"message": "School info retrieved successfully", "data": row}
    else:
        raise HTTPException(status_code=404, detail="School data not found")
    
@school_data.post("/classes")
async def get_classes(school_id_request: SchoolIdRequest, db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Query to get distinct classes for a specific SchoolId
    get_classes_query = """
    SELECT DISTINCT 
        nursery, LKG, UKG, class_1, class_2, class_3, class_4, class_5, class_6, class_7, class_8, class_9, class_10, class_11, class_12 
    FROM staffallocation 
    WHERE schoolid = %s
    """
    cursor.execute(get_classes_query, (school_id_request.SchoolId,))
    classes = cursor.fetchall()
    
    # Process the results
    class_list = []
    for class_data in classes:
        for key, value in class_data.items():
            if value:
                class_list.append(key.replace('_', ' ').title())
    
    return {"classes": class_list}

@school_data.post("/subjects")
async def get_subjects(school_id_request: SchoolIdRequest, db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Query to get distinct subjects for a specific SchoolId
    get_subjects_query = """
    SELECT DISTINCT subject 
    FROM staffallocation 
    WHERE schoolid = %s
    """
    cursor.execute(get_subjects_query, (school_id_request.SchoolId,))
    subjects = cursor.fetchall()
    
    subject_list = [subject['subject'] for subject in subjects]
    
    return {"subjects": subject_list}
# ...existing code...

# ...existing code...

@school_data.post("/teachers")
async def get_teachers(teacher_request: TeacherRequest, db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Log the incoming request
    logger.info(f"Received request for teachers with SchoolId: {teacher_request.SchoolId}, Class: {teacher_request.Class}, Subject: {teacher_request.Subject}")
    class1 = teacher_request.Class.replace(' ', '_').lower()
    print(class1)
    
    # Query to get the specific list of teachers for a class and subject
    get_teachers_query = f"""
    SELECT {class1}
    FROM staffallocation 
    WHERE schoolid = %s AND subject = %s 
    """
    cursor.execute(get_teachers_query, (teacher_request.SchoolId, teacher_request.Subject))
    result = cursor.fetchone()
    print(result)
    
    if result and class1 in result:
        class_data = json.loads(result[class1])
        teacher_list = class_data.get('teacherlist', [])
    else:
        teacher_list = []
    teachers = []
    for teacher_id in teacher_list:
        cursor.execute("SELECT UserId, Name FROM teachers WHERE UserId = %s", (teacher_id,))
        teacher = cursor.fetchone()
        if teacher:
            teachers.append({"userId": teacher["UserId"], "name": teacher["Name"]})
    
    # Log the result
    logger.info(f"Returning teachers: {teachers}")
    
    return {"teachers": teachers}

# ...existing code...

@school_data.post("/allottedteachers")
async def submit_allotted_teachers(request: AllottedTeachersRequest, db=Depends(get_db1)):
    cursor = db.cursor()

    for grade, subjects in request.AllottedTeachers.items():
        for subject, teacher_id in subjects.items():
            class_column = grade.replace(' ', '_').lower()
            get_allocation_query = f"SELECT {class_column} FROM staffallocation WHERE schoolid = %s AND subject = %s"
            cursor.execute(get_allocation_query, (request.SchoolId, subject))
            result = cursor.fetchone()

            if result:
                class_data = json.loads(result[0]) if result[0] else {"teacherlist": []}
                class_data['allocatedteacher'] = teacher_id
                update_allocation_query = f"UPDATE staffallocation SET {class_column} = %s WHERE schoolid = %s AND subject = %s"
                cursor.execute(update_allocation_query, (json.dumps(class_data), request.SchoolId, subject))
            else:
                # If no matching row exists, insert a new row
                insert_allocation_query = f"INSERT INTO staffallocation (schoolid, subject, {class_column}) VALUES (%s, %s, %s)"
                cursor.execute(insert_allocation_query, (request.SchoolId, subject, json.dumps({"teacherlist": [], "allocatedteacher": teacher_id})))

    db.commit()

    return {"message": "Allotted teachers updated successfully"}

@school_data.post("/class-subjects-teachers")
async def get_class_subjects_teachers(teacher_request: TeacherRequest, db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Log the incoming request
    logger.info(f"Received request for class subjects and teachers with SchoolId: {teacher_request.SchoolId}, Class: {teacher_request.Class}")
    class_column = teacher_request.Class.replace(' ', '_').lower()
    
    # Query to get the subjects and their allotted teachers for a specific SchoolId and Class
    get_subjects_teachers_query = f"""
    SELECT subject, {class_column}
    FROM staffallocation 
    WHERE schoolid = %s
    """
    cursor.execute(get_subjects_teachers_query, (teacher_request.SchoolId,))
    subjects_teachers = cursor.fetchall()
    
    result = []
    for item in subjects_teachers:
        class_data = json.loads(item[class_column])
        allocated_teacher_id = class_data.get('allocatedteacher')
        if allocated_teacher_id:
            cursor.execute("SELECT Name FROM teachers WHERE UserId = %s", (allocated_teacher_id,))
            teacher = cursor.fetchone()
            if teacher:
                result.append({"subject": item['subject'], "teacher": teacher["Name"]})
    
    # Log the result
    logger.info(f"Returning subjects and teachers: {result}")
    
    return {"subjects_teachers": result}

# ...existing code...