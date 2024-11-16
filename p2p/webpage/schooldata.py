from fastapi import APIRouter, HTTPException, Depends
from db import get_db1
from pydantic import BaseModel
import mysql.connector
from typing import List, Dict
import json

school_data = APIRouter()

class SchoolInternalData(BaseModel):
    SchoolId: str
    State: str
    SchoolType: str
    Curriculum: str
    OtherCurriculum: str
    GradeLevelFrom: str
    GradeLevelTo: str
    Subjects: List[str]
    Medium: str
    AcademicYearStart: str  # Format: YYYY-MM
    AcademicYearEnd: str    # Format: YYYY-MM
    ExtraPrograms: List[str]
    SchoolTimingFrom: str
    SchoolTimingTo: str
    ExamPattern: str
    OtherExamPattern: str
    AssessmentCriteria: str
    OtherAssessmentCriteria: str
    FeeStructure: List[Dict[str, str]]
    TotalAmount: float
    TeachingStaff: List[str]
    NonTeachingStaff: List[str]

class SchoolIdRequest(BaseModel):
    SchoolId: str

@school_data.post("/schooldata")
async def create_school_internal_data(details: SchoolInternalData, db=Depends(get_db1)):
    cursor = db.cursor()
    
    # Create schooldata table if not exists
    create_schooldata_table_query = """
    CREATE TABLE IF NOT EXISTS schooldata (
        id INT AUTO_INCREMENT PRIMARY KEY,
        SchoolId VARCHAR(255),
        State VARCHAR(255),
        SchoolType VARCHAR(255),
        Curriculum VARCHAR(255),
        OtherCurriculum VARCHAR(255),
        GradeLevelFrom VARCHAR(255),
        GradeLevelTo VARCHAR(255),
        Subjects JSON,
        Medium VARCHAR(255),
        AcademicYearStart VARCHAR(10),  # Format: YYYY-MM
        AcademicYearEnd VARCHAR(10),    # Format: YYYY-MM
        ExtraPrograms JSON,
        SchoolTimingFrom TIME,
        SchoolTimingTo TIME,
        ExamPattern VARCHAR(255),
        OtherExamPattern VARCHAR(255),
        AssessmentCriteria VARCHAR(255),
        OtherAssessmentCriteria VARCHAR(255),
        FeeStructure JSON,
        TotalAmount FLOAT,
        TeachingStaff JSON,
        NonTeachingStaff JSON
    )
    """
    cursor.execute(create_schooldata_table_query)
    
    # Insert values into schooldata table
    insert_schooldata_query = """
    INSERT INTO schooldata (
        SchoolId, State, SchoolType, Curriculum, OtherCurriculum, GradeLevelFrom, GradeLevelTo, Subjects, Medium,
        AcademicYearStart, AcademicYearEnd, ExtraPrograms, SchoolTimingFrom, SchoolTimingTo, ExamPattern,
        OtherExamPattern, AssessmentCriteria, OtherAssessmentCriteria, FeeStructure, TotalAmount, TeachingStaff, NonTeachingStaff
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_schooldata_query, (
        details.SchoolId, details.State, details.SchoolType, details.Curriculum, details.OtherCurriculum,
        details.GradeLevelFrom, details.GradeLevelTo, json.dumps(details.Subjects), details.Medium,
        details.AcademicYearStart, details.AcademicYearEnd, json.dumps(details.ExtraPrograms),
        details.SchoolTimingFrom, details.SchoolTimingTo, details.ExamPattern, details.OtherExamPattern,
        details.AssessmentCriteria, details.OtherAssessmentCriteria, json.dumps(details.FeeStructure),
        details.TotalAmount, json.dumps(details.TeachingStaff), json.dumps(details.NonTeachingStaff)
    ))
    
    db.commit()
    
    return {"message": "Details updated successfully"}

@school_data.post("/schoolinfo")
async def get_school_info(school_id_request: SchoolIdRequest, db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Query to get the row that matches the given SchoolId
    get_schooldata_query = "SELECT * FROM schooldata WHERE SchoolId = %s"
    cursor.execute(get_schooldata_query, (school_id_request.SchoolId,))
    
    # Fetch the row
    row = cursor.fetchone()
    
    if row:
        # Convert JSON fields back to Python objects
        row['Subjects'] = json.loads(row['Subjects'])
        row['ExtraPrograms'] = json.loads(row['ExtraPrograms'])
        row['FeeStructure'] = json.loads(row['FeeStructure'])
        row['TeachingStaff'] = json.loads(row['TeachingStaff'])
        row['NonTeachingStaff'] = json.loads(row['NonTeachingStaff'])
        return {"message": "School info retrieved successfully", "data": row}
    else:
        raise HTTPException(status_code=404, detail="School data not found")