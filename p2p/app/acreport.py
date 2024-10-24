from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
from pydantic import BaseModel
import mysql.connector
import json
from typing import List, Dict

class ACReportDetails(BaseModel):
    schoolId: str
    year: str
    exam: str
    studentId: str

acreport_router = APIRouter()

@acreport_router.post("/acreport")
async def get_academic_report(details: ACReportDetails):
    if details.year == "23-24": year="2324"
    esle: year =details.year
    table_name = f"Y{details.year}_{details.schoolId}".replace("-", "")
    print(table_name)
    db = get_db1()
    cursor = db.cursor()

    
    # Use parameterized query and escape column name
    select_query = f"SELECT {details.exam} FROM {table_name} WHERE `STUDENT_ID` = %s"
    cursor.execute(select_query, (details.studentId,))
    result = cursor.fetchone()
    print("e2", result)
    
    if result:
        student_exam_data = result[0]
        if student_exam_data:
            student_exam_dict = json.loads(student_exam_data)
            return student_exam_dict
        else:
            raise HTTPException(status_code=404, detail="No data found for the specified exam")
    else:
        raise HTTPException(status_code=404, detail=f"Student with ID {details.studentId} not found")
    