from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
import pyodbc
from pydantic import BaseModel

stl_router = APIRouter()

class StudentLogin(BaseModel):
    studentId: str
    password: str

@stl_router.post("/st_login")
async def teacher_login(student: StudentLogin, db=Depends(get_db1)):
    studentId = student.studentId
    password = student.password
    print(studentId, password)

    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM students WHERE STUDENT_ID = '{studentId}' AND PASSWORD = '{password}'")
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=400, detail="Invalid teacherId or password")

    return {"message": "Login successful", "schoolId": row.SCHOOL_ID}