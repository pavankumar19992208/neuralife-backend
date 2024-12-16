from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
import mysql.connector
from pydantic import BaseModel
import json

tl_router = APIRouter()

class TeacherLogin(BaseModel):
    userId: str
    password: str

@tl_router.post("/teacher_login")
async def teacher_login(teacher: TeacherLogin, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    teacherId = teacher.userId
    password = teacher.password
    print(teacherId, password)
    
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM teachers WHERE UserId = %s AND password = %s", (teacherId, password))
    teacher_row = cursor.fetchone()
    
    if teacher_row is None:
        print("Not found")
        raise HTTPException(status_code=400, detail="Invalid teacherId or password")
    
    teacher_dict = {column[0]: value for column, value in zip(cursor.description, teacher_row)}
    
    cursor.execute("SELECT Name FROM teachers WHERE userid = %s", (teacherId,))
    teacher_details = cursor.fetchone()
    
    cursor.execute("SELECT subjectSpecialization FROM teachers WHERE userid = %s", (teacherId,))
    subject_specialization = cursor.fetchone()[0]
    
    cursor.execute("SELECT SCHOOL_NAME FROM schools WHERE SCHOOL_ID = %s", (teacher_row[2],))  # Assuming SCHOOL_ID is the third column
    school_name = cursor.fetchone()[0]
    
    teacher_dict.update({
        "SCHOOL_NAME": school_name,
        "user_type": "teacher",
        "subjectSpecialization": json.loads(subject_specialization)
    })
    print(teacher_dict)
    return {"message": "Login successful", "user": teacher_dict}


@tl_router.post("/testerlogin")
async def teacher_login(tester: TeacherLogin, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    teacherId = tester.userId
    password = tester.password
    print(teacherId, password)
    
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM  slinkedinusers WHERE UserId = %s", (teacherId,))
    tester_row = cursor.fetchone()
    
    if tester_row is None:
        print("Not found")
        raise HTTPException(status_code=400, detail="Invalid userId")
    
    tester_dict = {column[0]: value for column, value in zip(cursor.description, tester_row)}
    

    tester_dict.update({
        "SCHOOL_NAME": "tester_school",
        "user_type": "tester",
    })
    print(tester_dict)
    return {"message": "Login successful", "user": tester_dict}