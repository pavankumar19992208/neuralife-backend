from fastapi import APIRouter, HTTPException, Depends
from shared.db import get_db1
from pydantic import BaseModel
import mysql.connector
import json
from typing import List, Dict

class Marks(BaseModel):
    marks: str
    r_no: int
    student_name: str

class StudentDetails(BaseModel):
    schoolId: str
    year: str
    Tmarks: List[Marks]
    exam: str
    grade: str
    section: str
    subject: str

upm_router = APIRouter()

@upm_router.post("/upmarks")
async def get_student_details(details: StudentDetails):
    table_name = f"Y{details.year}_{details.schoolId}"
    db = get_db1()
    cursor = db.cursor()
    print("e1")
    
    # Iterate over each mark and update the corresponding row in the database
    for mark in details.Tmarks:
        # Retrieve the current value of the exam column for the specific student
        select_query = f"SELECT {details.exam} FROM {table_name} WHERE R_NO = %s AND GRADE = %s AND SECTION = %s"
        cursor.execute(select_query, (mark.r_no, details.grade, details.section))
        result = cursor.fetchone()
        
        if result:
            student_exam_data = result[0]
            if student_exam_data:
                student_exam_dict = json.loads(student_exam_data)
            else:
                student_exam_dict = {}
            
            # Update the student's exam data with the new subject:marks pair
            student_exam_dict[details.subject] = mark.marks
            updated_student_exam_data = json.dumps(student_exam_dict)
            
            # Ensure all results are read before executing the next query
            cursor.fetchall()
            
            # Update the exam column in the database for the specific student
            update_query = f"UPDATE {table_name} SET {details.exam} = %s WHERE R_NO = %s AND GRADE = %s AND SECTION = %s"
            cursor.execute(update_query, (updated_student_exam_data, mark.r_no, details.grade, details.section))
        else:
            raise HTTPException(status_code=404, detail=f"Student with R_NO {mark.r_no}, GRADE {details.grade}, and SECTION {details.section} not found")
    
    # Commit the transaction
    db.commit()
    print("ef")
    
    return {"message": "Marks updated successfully"}