from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
import pyodbc
from pydantic import BaseModel


class RollNumberDetails(BaseModel):
    schoolId: str
    grade: str
    section: str

rl_router = APIRouter()

@rl_router.post("/rlno")
async def generate_roll_numbers(details: RollNumberDetails, db=Depends(get_db1)):
    cursor = db.cursor()

    cursor.execute("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'students' AND COLUMN_NAME = 'R_NO'")
    r_no_exists = cursor.fetchone()

    # Add R_NO column if it doesn't exist
    if not r_no_exists:
        cursor.execute("ALTER TABLE students ADD R_NO int")

    # Get the students with the same school_id, grade, and section, ordered by name
    cursor.execute("SELECT STUDENT_ID, STUDENT_NAME FROM students WHERE SCHOOL_ID = ? AND GRADE = ? AND SECTION = ? AND R_NO IS NULL ORDER BY STUDENT_NAME", (details.schoolId, details.grade, details.section))
    students = cursor.fetchall()

    if not students:
        cursor.execute("SELECT R_NO, GRADE, SECTION, STUDENT_NAME FROM students WHERE SCHOOL_ID = ? AND GRADE = ? AND SECTION = ? ORDER BY R_NO", (details.schoolId, details.grade, details.section))
        students_table = cursor.fetchall()

    # Convert to list of dictionaries
        students_table = [dict(zip(["R_NO", "GRADE", "SECTION", "STUDENT_NAME"], student)) for student in students_table]
 
        return {"message": "Roll numbers have been generated ", "students": students_table}

    # Generate and update roll numbers for these students
    for i, student in enumerate(students, start=1):
        cursor.execute("UPDATE students SET R_NO = ? WHERE STUDENT_ID = ?", (i, student[0]))

    # Commit the changes
    db.commit()

    # Get the updated students table
    # Get the updated students table
    cursor.execute("SELECT R_NO, GRADE, SECTION, STUDENT_NAME FROM students WHERE SCHOOL_ID = ? AND GRADE = ? AND SECTION = ? ORDER BY R_NO", (details.schoolId, details.grade, details.section))
    students_table = cursor.fetchall()
    
    # Convert to list of dictionaries
    students_table = [dict(zip(["R_NO", "GRADE", "SECTION", "STUDENT_NAME"], student)) for student in students_table]

    return {"message": "Roll numbers generated successfully", "students": students_table}