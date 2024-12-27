from fastapi import APIRouter, HTTPException, Depends
from shared.db import get_db1
import mysql.connector
from pydantic import BaseModel
from typing import Dict, List, Optional

ct_router = APIRouter()

class Period(BaseModel):
    from_time: str
    to_time: str
    subject: str
    teacher: Optional[str] = None

class DaySchedule(BaseModel):
    periods: Dict[str, Period]

class ClassTimeTable(BaseModel):
    SchoolId: str
    class_name: str
    Monday: DaySchedule
    Tuesday: DaySchedule
    Wednesday: DaySchedule
    Thursday: DaySchedule
    Friday: DaySchedule
    Saturday: DaySchedule

@ct_router.post("/classtimetable")
async def create_class_timetable(timetable: ClassTimeTable, db=Depends(get_db1)):
    cursor = db.cursor()
    
    # Create classtime table if not exists
    create_classtime_table_query = """
    CREATE TABLE IF NOT EXISTS classtime (
        id INT AUTO_INCREMENT PRIMARY KEY,
        SchoolId VARCHAR(255),
        class_name VARCHAR(255),
        day VARCHAR(50),
        period VARCHAR(50),
        from_time TIME,
        to_time TIME,
        subject VARCHAR(255),
        teacher VARCHAR(255)
    )
    """
    cursor.execute(create_classtime_table_query)
    
    # Delete existing timetable for the given SchoolId and class_name
    delete_existing_timetable_query = """
    DELETE FROM classtime WHERE SchoolId = %s AND class_name = %s
    """
    cursor.execute(delete_existing_timetable_query, (timetable.SchoolId, timetable.class_name))
    
    # Insert new timetable data into classtime table
    for day, schedule in timetable.dict().items():
        if day in ["SchoolId", "class_name"]:
            continue
        for period_num, period in schedule['periods'].items():
            insert_period_query = """
            INSERT INTO classtime (SchoolId, class_name, day, period, from_time, to_time, subject, teacher)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_period_query, (
                timetable.SchoolId, timetable.class_name, day, period_num, period['from_time'], period['to_time'], period['subject'], period.get('teacher')
            ))
    
    db.commit()
    
    return {"message": "Timetable updated successfully"}

# Add the router to your main application
from fastapi import FastAPI

app = FastAPI()

app.include_router(ct_router)