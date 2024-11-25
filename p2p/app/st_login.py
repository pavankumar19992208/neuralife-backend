from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
import pyodbc
from pydantic import BaseModel

stl_router = APIRouter()

class StudentLogin(BaseModel):
    userId: str
    password: str

@stl_router.post("/st_login")
async def teacher_login(student: StudentLogin, db=Depends(get_db1)):
    studentId = student.userId
    password = student.password
    print(studentId, password)

    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM student WHERE StudentId = '{studentId}' AND Password = '{password}'")
    row = cursor.fetchone()
    student_dict = {column[0]: value for column, value in zip(cursor.description, row)}
    cursor.execute("SELECT SCHOOL_NAME FROM schools WHERE SCHOOL_ID = %s", (row[0],))  # Assuming SCHOOL_ID is the third column
    school_name = cursor.fetchone()[0]

    student_dict.update({
        "SCHOOL_NAME": school_name,
    })
    if row is None:
        raise HTTPException(status_code=400, detail="Invalid teacherId or password")

    return {"message": "Login successful", "student":student_dict}