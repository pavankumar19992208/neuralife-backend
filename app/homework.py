from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from shared.db import get_db1
import mysql.connector
from typing import Optional, Dict, List
from datetime import date
import json

homework_router = APIRouter()

class HomeworkDetails(BaseModel):
    SchoolId: str
    H_id: Optional[int] = None  # Auto-incremented primary key
    Class_: str
    Sec: str
    Subject: str
    HomeWork: Dict[str, Optional[str]]  # JSON field to store title, description, and attachment_url
    CreatedAt: date
    DueDate: date
    UpdatedBy: str

class AttendanceDetails(BaseModel):
    student_id: int
    date: date
    status: str
    remarks: Optional[str] = None
    recorded_by: str

class AttendanceList(BaseModel):
    attendance: List[AttendanceDetails]

@homework_router.post("/homework")
async def create_homework(details: HomeworkDetails, db=Depends(get_db1)):
    cursor = db.cursor()
    
    # Create homework table if not exists
    create_homework_table_query = """
    CREATE TABLE IF NOT EXISTS homework (
        H_id INT AUTO_INCREMENT PRIMARY KEY,
        SchoolId VARCHAR(255),
        class_ VARCHAR(255),
        sec VARCHAR(255),
        subject VARCHAR(255),
        HomeWork JSON,
        CreatedAt DATE,
        DueDate DATE,
        UpdatedBy VARCHAR(255)
    )
    """
    cursor.execute(create_homework_table_query)
    
    # Insert values into homework table
    insert_homework_query = """
    INSERT INTO homework (
        SchoolId, class_, sec, subject, HomeWork, CreatedAt, DueDate, UpdatedBy
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_homework_query, (
        details.SchoolId, details.Class_, details.Sec, details.Subject, json.dumps(details.HomeWork),
        details.CreatedAt, details.DueDate, details.UpdatedBy
    ))
    
    # Get the last inserted H_id
    cursor.execute("SELECT LAST_INSERT_ID()")
    last_inserted_id = cursor.fetchone()[0]
    print("Last inserted H_id:", last_inserted_id)
    
    # Create currenthw table if not exists
    create_currenthw_table_query = """
    CREATE TABLE IF NOT EXISTS currenthw (
        Ch_id INT AUTO_INCREMENT PRIMARY KEY,
        H_id INT,
        SchoolId VARCHAR(255),
        class_ VARCHAR(255),
        sec VARCHAR(255),
        subject VARCHAR(255),
        HomeWork JSON,
        CreatedAt DATE,
        DueDate DATE,
        UpdatedBy VARCHAR(255)
    )
    """
    cursor.execute(create_currenthw_table_query)
    print("Created currenthw table if not exists")
    
    # Check if a record with the same SchoolId, class_, sec, and subject exists in currenthw
    cursor.execute("""
    SELECT Ch_id FROM currenthw WHERE SchoolId = %s AND class_ = %s AND sec = %s AND subject = %s
    """, (details.SchoolId, details.Class_, details.Sec, details.Subject))
    existing_record = cursor.fetchone()
    print("Existing record:", existing_record)
    
    if existing_record:
        print("Updating existing record")
        # Update the existing record
        update_currenthw_query = """
        UPDATE currenthw SET H_id = %s, HomeWork = %s, CreatedAt = %s, DueDate = %s, UpdatedBy = %s
        WHERE Ch_id = %s
        """
        cursor.execute(update_currenthw_query, (
            last_inserted_id, json.dumps(details.HomeWork), details.CreatedAt, details.DueDate, details.UpdatedBy,
            existing_record[0]
        ))
    else:
        print("Inserting new record into currenthw")
        # Insert new record into currenthw
        insert_currenthw_query = """
        INSERT INTO currenthw (
            H_id, SchoolId, class_, sec, subject, HomeWork, CreatedAt, DueDate, UpdatedBy
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        print("Parameters for insert:", (
            last_inserted_id, details.SchoolId, details.Class_, details.Sec, details.Subject, json.dumps(details.HomeWork),
            details.CreatedAt, details.DueDate, details.UpdatedBy
        ))
        cursor.execute(insert_currenthw_query, (
            last_inserted_id, details.SchoolId, details.Class_, details.Sec, details.Subject, json.dumps(details.HomeWork),
            details.CreatedAt, details.DueDate, details.UpdatedBy
        ))
        print("Inserted new record into currenthw")
    
    db.commit()
    
    return {"message": "Homework created/updated successfully"}

@homework_router.post("/attendance")
async def create_attendance(details: AttendanceList, db=Depends(get_db1)):
    cursor = db.cursor()
    
    # Create attendance table if not exists
    create_attendance_table_query = """
    CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        date DATE,
        status ENUM('P', 'AB'),
        remarks TEXT,
        recorded_by VARCHAR(255)
    )
    """
    
    cursor.execute(create_attendance_table_query)
    
    # Insert values into attendance table
    insert_attendance_query = """
    INSERT INTO attendance (
        student_id, date, status, remarks, recorded_by
    ) VALUES (%s, %s, %s, %s, %s)
    """
    
    for record in details.attendance:
        # Ensure status is either 'P' or 'AB'
        if record.status not in ['P', 'AB']:
            raise HTTPException(status_code=400, detail=f"Invalid status value: {record.status}")
        
        cursor.execute(insert_attendance_query, (
            record.student_id, record.date, record.status, record.remarks, record.recorded_by
        ))
    
    db.commit()
    
    return {"message": "Attendance records created successfully"}