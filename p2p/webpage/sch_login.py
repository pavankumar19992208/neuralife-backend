from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
import pyodbc
from pydantic import BaseModel
import mysql.connector

class SchoolLogin(BaseModel):
    schoolId: str
    password: str

schl_router = APIRouter()

@schl_router.post("/sch_login")
async def school_login(school: SchoolLogin):
    schoolId = school.schoolId
    password = school.password

    db = get_db1()
    cursor = db.cursor()

    # Use parameterized query to prevent SQL injection
    cursor.execute("SELECT SCHOOL_ID, SCHOOL_NAME FROM schools WHERE SCHOOL_ID = %s AND PASSWORD = %s", (schoolId, password))
    row = cursor.fetchone()
   
    if row is None:
        raise HTTPException(status_code=400, detail="Invalid schoolId or password")
    return {"message":"login successfull","SCHOOL_ID": row[0], "SCHOOL_NAME": row[1]}