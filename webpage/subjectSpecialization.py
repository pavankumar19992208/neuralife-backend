from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
import mysql.connector
import json
from db import get_db1

allocation_router = APIRouter()

class TeacherAllocation(BaseModel):
    subject: str
    subject_id: int  # Add subject_id field
    class_teachers: Dict[str, List[str]]  # Dictionary with class as key and list of teachers as value

@allocation_router.post("/allocate")
async def allocate_teacher(allocation: TeacherAllocation, db=Depends(get_db1)):
    try:
        cursor = db.cursor()
        
        # Create table if not exists
        create_allocation_table(db)
        
        # Prepare the data for insertion
        subjects = allocation.subjects  # Assuming subjects is a list of subjects from the payload
        
        for subject in subjects:
            data = {
                "subject": subject,
                "subject_id": allocation.subject_id,  # Include subject_id in data
                "class_1": json.dumps(allocation.class_teachers.get("class_1", [])),
                "class_2": json.dumps(allocation.class_teachers.get("class_2", [])),
                "class_3": json.dumps(allocation.class_teachers.get("class_3", [])),
                "class_4": json.dumps(allocation.class_teachers.get("class_4", [])),
                "class_5": json.dumps(allocation.class_teachers.get("class_5", [])),
                "class_6": json.dumps(allocation.class_teachers.get("class_6", [])),
                "class_7": json.dumps(allocation.class_teachers.get("class_7", [])),
                "class_8": json.dumps(allocation.class_teachers.get("class_8", [])),
                "class_9": json.dumps(allocation.class_teachers.get("class_9", [])),
                "class_10": json.dumps(allocation.class_teachers.get("class_10", [])),
                "class_11": json.dumps(allocation.class_teachers.get("class_11", [])),
                "class_12": json.dumps(allocation.class_teachers.get("class_12", []))
            }

            # Insert data into the table
            insert_query = """
            INSERT INTO teacher_allocation (
                subject, subject_id, class_1, class_2, class_3, class_4, class_5, class_6, class_7, class_8, class_9, class_10, class_11, class_12
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                data["subject"], data["subject_id"], data["class_1"], data["class_2"], data["class_3"], data["class_4"], data["class_5"], data["class_6"],
                data["class_7"], data["class_8"], data["class_9"], data["class_10"], data["class_11"], data["class_12"]
            ))
        
        db.commit()
        
        return {"message": "Teacher allocation added successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

def create_allocation_table(db):
    cursor = db.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS teacher_allocation (
        id INT AUTO_INCREMENT PRIMARY KEY,
        subject VARCHAR(255),
        subject_id INT,
        class_1 JSON,
        class_2 JSON,
        class_3 JSON,
        class_4 JSON,
        class_5 JSON,
        class_6 JSON,
        class_7 JSON,
        class_8 JSON,
        class_9 JSON,
        class_10 JSON,
        class_11 JSON,
        class_12 JSON
    )
    """
    cursor.execute(create_table_query)
    db.commit()