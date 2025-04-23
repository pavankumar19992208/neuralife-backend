from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
from pydantic import BaseModel
import mysql.connector
from typing import List, Dict, Optional, Union
import json
import logging
from datetime import time

school_data = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 
class SchoolInternalData(BaseModel):
    school_id: str
    school_type: str
    curriculum: str
    other_curriculum: Optional[str] = None
    medium: str
    academic_year_start: str
    academic_year_end: str
    school_timing_from: time
    school_timing_to: time
    exam_pattern: Optional[Union[str, int]] = None
    assessment_criteria: Optional [str] = None
    other_assessment_criteria: Optional[str] = None
    other_exam_pattern: Optional[str] = None
    state: Optional[str] = None

class SchoolIdRequest(BaseModel):
    school_id: str

class TeacherRequest(BaseModel):
    SchoolId: str
    Class: str
    Subject: Optional[str] = None

class AllottedTeachersRequest(BaseModel):
    SchoolId: str
    AllottedTeachers: Dict[str, Dict[str, str]]

class Activity(BaseModel):
    activity_id: int
    activity_name: str

@school_data.post("/schooldata")
async def submit_school_type(data: SchoolInternalData, db=Depends(get_db1)):
    try:
        cursor = db.cursor()
        
        # Print received data
        print("Received school type data:", data.dict())
        
        
        # Insert only school type
        cursor.execute("""
        INSERT INTO school_data (school_id, school_type, curriculum, medium, academic_year_start,
                        academic_year_end, school_timing_from, school_timing_to, exam_pattern, assessment_criteria,
                        other_exam_pattern, state, other_curriculum, other_assessment_criteria)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (data.school_id, data.school_type, data.curriculum, data.medium, data.academic_year_start,
               data.academic_year_end, data.school_timing_from, data.school_timing_to, data.exam_pattern, data.assessment_criteria,
               data.other_exam_pattern, data.state, data.other_curriculum, data.other_assessment_criteria))
        
        db.commit()
        
        return {"message": "School type saved successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@school_data.get("/active-activities", response_model=List[Activity])
async def get_active_activities(db=Depends(get_db1)):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT activity_id, activity_name 
            FROM school_activities 
            WHERE is_active = 1
        """)
        activities = cursor.fetchall()
        return activities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# @school_data.post("/schoolinfo")
# async def get_school_info(school_id_request: SchoolIdRequest, db=Depends(get_db1)):
#     cursor = db.cursor(dictionary=True)
    
#     # Query to get the row that matches the given SchoolId
#     get_schooldata_query = "SELECT * FROM schooldata WHERE SchoolId = %s"
#     cursor.execute(get_schooldata_query, (school_id_request.SchoolId,))
    
#     # Fetch the row
#     row = cursor.fetchone()
    
#     if row:
#         # Convert JSON fields back to Python objects
#         row['Subjects'] = json.loads(row['Subjects'])
#         row['ExtraPrograms'] = json.loads(row['ExtraPrograms'])
#         row['FeeStructure'] = json.loads(row['FeeStructure'])
#         row['TeachingStaff'] = json.loads(row['TeachingStaff'])
#         row['NonTeachingStaff'] = json.loads(row['NonTeachingStaff'])
#         row['GradesOffered'] = json.loads(row['GradesOffered'])  # Ensure GradesOffered is included
#         return {"message": "School info retrieved successfully", "data": row}
#     else:
#         raise HTTPException(status_code=404, detail="School data not found")

@school_data.post("/schoolinfo")
async def get_school_info(school_id_request: SchoolIdRequest, db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    query = "SELECT * FROM school_data WHERE school_id = %s"
    cursor.execute(query, (school_id_request.school_id,))
    
    row = cursor.fetchone()
    
    if row:
        # Convert JSON fields and maintain snake_case keys
        return {
            "message": "School info retrieved successfully",
            "data": {
                "school_id": row["school_id"],
                "state": row["state"],
                "school_type": row["school_type"],
                "curriculum": row["curriculum"],
                "other_curriculum": row["other_curriculum"],
                "grade_level_from": row["grade_level_from"],
                "grade_level_to": row["grade_level_to"],
                "subjects": json.loads(row["subjects"]),
                "medium": row["medium"],
                "academic_year_start": row["academic_year_start"],
                "academic_year_end": row["academic_year_end"],
                "extra_programs": json.loads(row["extra_programs"]),
                "school_timing_from": row["school_timing_from"],
                "school_timing_to": row["school_timing_to"],
                "exam_pattern": row["exam_pattern"],
                "other_exam_pattern": row["other_exam_pattern"],
                "assessment_criteria": row["assessment_criteria"],
                "other_assessment_criteria": row["other_assessment_criteria"],
                "fee_structure": json.loads(row["fee_structure"]),
                "total_amount": row["total_amount"],
                "teaching_staff": json.loads(row["teaching_staff"]),
                "non_teaching_staff": json.loads(row["non_teaching_staff"]),
                "grades_offered": json.loads(row["grades_offered"])
            }
        }
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

# ...existing code...

# @school_data.post("/schoolinfo")
# async def get_school_info(school_id_request: SchoolIdRequest, db=Depends(get_db1)):
#     cursor = db.cursor(dictionary=True)
    
#     # Query to get the row that matches the given SchoolId
#     get_schooldata_query = "SELECT * FROM schooldata WHERE SchoolId = %s"
#     cursor.execute(get_schooldata_query, (school_id_request.SchoolId,))
    
#     # Fetch the row
#     row = cursor.fetchone()
    
#     if row:
#         # Convert JSON fields back to Python objects
#         row['Subjects'] = json.loads(row['Subjects'])
#         row['ExtraPrograms'] = json.loads(row['ExtraPrograms'])
#         row['FeeStructure'] = json.loads(row['FeeStructure'])
#         row['TeachingStaff'] = json.loads(row['TeachingStaff'])
#         row['NonTeachingStaff'] = json.loads(row['NonTeachingStaff'])
#         row['GradesOffered'] = json.loads(row['GradesOffered'])
#         return {"message": "School info retrieved successfully", "data": row}
#     else:
#         raise HTTPException(status_code=404, detail="School data not found")

# ...existing code...
@school_data.get("/active-school-types")
async def get_active_school_types(db=Depends(get_db1)):
    try:
        cursor = db.cursor(dictionary=True)
        query = "SELECT type_name, typical_grades FROM school_types WHERE is_active = 1"
        cursor.execute(query)
        active_types = cursor.fetchall()
        
        if not active_types:
            logger.warning("No active school types found")
            
        return {
            "school_types": [
                {
                    "name": t["type_name"],
                    "grades": t["typical_grades"]
                } for t in active_types
            ]
        }
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

@school_data.get("/active-exam-patterns")
async def get_active_exam_patterns(db=Depends(get_db1)):
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT pattern_id, pattern_name, grading_system, term_structure 
            FROM exam_patterns 
            WHERE is_active = 1
        """
        cursor.execute(query)
        patterns = cursor.fetchall()
        
        if not patterns:
            logger.warning("No active exam patterns found")
            
        return {
            "exam_patterns": [
                {
                    "id": p["pattern_id"],
                    "name": p["pattern_name"],
                    "grading": p["grading_system"],
                    "term": p["term_structure"]
                } for p in patterns
            ]
        }
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

@school_data.get("/active-subjects")
async def get_active_subjects(db=Depends(get_db1)):
    try:
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT subject_id, subject_name, subject_code, subject_type 
            FROM subjects 
            WHERE is_active = 1
            ORDER BY subject_name
        """
        cursor.execute(query)
        subjects = cursor.fetchall()
        
        if not subjects:
            logger.warning("No active subjects found")
            
        return {
            "subjects": [
                {
                    "id": s["subject_id"],
                    "name": s["subject_name"],
                    "code": s["subject_code"],
                    "type": s["subject_type"]
                } for s in subjects
            ]
        }
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

@school_data.get("/staff-roles")
async def get_staff_roles(db=Depends(get_db1)):
    try:
        cursor = db.cursor(dictionary=True)
        
        # Get teaching roles (is_teaching_role = 1)
        teaching_query = "SELECT role_id, role_name FROM school_roles WHERE is_teaching_role = 1 ORDER BY role_name"
        cursor.execute(teaching_query)
        teaching_roles = cursor.fetchall()
        
        # Get non-teaching staff roles (is_staff = 1 AND is_teaching_role = 0)
        non_teaching_query = "SELECT role_id, role_name FROM school_roles WHERE is_staff = 1 AND is_teaching_role = 0 ORDER BY role_name"
        cursor.execute(non_teaching_query)
        non_teaching_roles = cursor.fetchall()
        
        return {
            "teaching_roles": [{"id": r["role_id"], "name": r["role_name"]} for r in teaching_roles],
            "non_teaching_roles": [{"id": r["role_id"], "name": r["role_name"]} for r in non_teaching_roles]
        }
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")