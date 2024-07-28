from fastapi import APIRouter, HTTPException, Depends
# from db import get_db1
import pyodbc
from pydantic import BaseModel

tl_router = APIRouter()

class TeacherLogin(BaseModel):
    teacherId: str
    password: str

@tl_router.post("/teacher_login")
async def teacher_login(teacher: TeacherLogin):
    # teacherId = teacher.teacherId
    # password = teacher.password
    # print(teacherId, password)
    # cursor = db.cursor()
    # cursor.execute("SELECT TEACHER_NAME FROM teachers WHERE TEACHER_ID = ?", (teacherId,))
    # teacher_name = cursor.fetchone()[0]
    # cursor.execute("SELECT SUBJECT FROM subjects WHERE TEACHER_ID = ?", (teacherId,))
    # subjects = [row[0] for row in cursor.fetchall()]


    # cursor.execute(f"SELECT * FROM teachers WHERE TEACHER_ID = '{teacherId}' AND PASSWORD = '{password}'")
    # r = cursor.fetchone()
    
    # cursor.execute("SELECT SCHOOL_NAME FROM schools WHERE SCHOOL_ID = ?", (r.SCHOOL_ID,))
    # school_name = cursor.fetchone()[0]
    
    # if r is None:
    #     raise HTTPException(status_code=400, detail="Invalid teacherId or password")
    
    # return {"message": "Login successful", "schoolId": r.SCHOOL_ID,"schoolName": school_name, "teacherName": teacher_name, "subjects": subjects}
    return {"message": "Login successful", "schoolId": "CHGA109182","schoolName": "CHAITANYA PUBLIC SCHOOL", "teacherName": "PAVAN", "subjects":["ENGLISH","TELUGU","MATHS"]}