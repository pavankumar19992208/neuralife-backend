# from fastapi import APIRouter, HTTPException, Depends
# from db import get_db1
# import pyodbc
# from pydantic import BaseModel

# class student_details(BaseModel):
#     schoolId: str
#     grade: str
#     section: str

# std_router = APIRouter()



# @std_router.post("/stdetails")
# async def get_student_details(details: student_details, db=Depends(get_db1)):
#     cursor = db.cursor()
#     cursor.execute("SELECT * FROM students WHERE SCHOOL_ID = ? AND GRADE = ? AND SECTION = ?", (details.schoolId, details.grade, details.section))
#     students_table = cursor.fetchall()
#     print(students_table)
#     students_table = [dict(zip(["SCHOOL_ID","STUDENT_ID", "STUDENT_NAME", "GRADE", "SECTION","","","","","","", "PASSWORD","R_NO"], student)) for student in students_table]
#     print(students_table)
#     return {"students": students_table}

from fastapi import APIRouter
from pydantic import BaseModel
import random
import string

class student_details(BaseModel):
    schoolId: str
    grade: str
    section: str

std_router = APIRouter()

def random_string(length: int):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def random_name():
    names = ["Aarav", "Vivaan", "Aditya", "Pranav", "Aryan", "Dhruv", "Arjun", "Atharv", "Rudra", "Sai"]
    return random.choice(names)

@std_router.post("/stdetails")
async def get_student_details(details: student_details):
    students_table = [
        {
            "SCHOOL_ID": details.schoolId,
            "STUDENT_ID": "STCH{:06d}".format(random.randint(1, 999999)),
            "STUDENT_NAME": random_name(),
            "GRADE": details.grade,
            "SECTION": details.section,
            "PASSWORD": random_string(10),
            "R_NO": random.randint(1, 100)
        } for _ in range(5)
    ]
    return {"students": students_table}