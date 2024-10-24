from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
from pydantic import BaseModel
import mysql.connector

class StudentDetails(BaseModel):
    year: str
    schoolId: str
    grade: str
    section: str
std_router = APIRouter()

@std_router.post("/stdetails")
async def get_student_details(details: StudentDetails):
    table_name = f"Y{details.year}_{details.schoolId}"
    print(table_name)
    db = get_db1()
    cursor = db.cursor()
    
    # Use %s as placeholders for MySQL
    query = f"SELECT * FROM {table_name} WHERE GRADE = %s AND SECTION = %s"
    cursor.execute(query, (details.grade, details.section))
    
    students_table = cursor.fetchall()
    print(students_table)
    
    # Correct the column names in the zip function
    column_names = ["STUDENT_ID", "STUDENT_NAME", "GRADE", "SECTION", "R_NO", "FA1", "FA2", "SA1", "FA3", "FA4", "SA2", "CP", "GD"]
    students_table = [dict(zip(column_names, student)) for student in students_table]
    
    # Filter out unwanted columns
    filtered_students_table = [
        {key: student[key] for key in ["STUDENT_ID", "STUDENT_NAME", "GRADE", "SECTION", "R_NO"]}
        for student in students_table
    ]
    
    print(filtered_students_table)
    return {"students": filtered_students_table}