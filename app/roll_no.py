from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from db import get_db1
import mysql.connector
from pydantic import BaseModel

class RollNumberDetails(BaseModel):
    schoolId: str
    year: str
    grade: str
    section: str

app = FastAPI()
rl_router = APIRouter()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "details": exc.errors()},
    )

@rl_router.post("/rlno")
async def generate_roll_numbers(details: RollNumberDetails):
    db = get_db1()
    cursor = db.cursor()
    
    # Construct the table name and enclose it in backticks
    table_name = f"`Y{details.year}_{details.schoolId}`"
    
    # create_address_table_query = f"""
    # CREATE TABLE IF NOT EXISTS {table_name} (
    #             STUDENT_ID NVARCHAR(50),
    #             STUDENT_NAME NVARCHAR(100),
    #             GRADE NVARCHAR(10),
    #             SECTION NVARCHAR(10),
    #             R_NO INT,
    #             FA1 FLOAT,
    #             FA2 FLOAT,
    #             SA1 FLOAT,
    #             FA3 FLOAT,
    #             FA4 FLOAT,
    #             SA2 FLOAT,
    #             CP FLOAT,
    #             GD FLOAT
    #         )
    # """
    # cursor.execute(create_address_table_query)    
    try:    
        # Select rows from the new table where GRADE and SECTION match the provided details
        select_new_table_query = f"""
        SELECT STUDENT_ID
        FROM {table_name}
        WHERE GRADE = %s AND SECTION = %s
        """
        cursor.execute(select_new_table_query, (details.grade, details.section))
        new_rows = cursor.fetchall()
        print(new_rows)
        # Update each row with a unique roll number starting from 1
        roll_number = 1
        for new_row in new_rows:
            update_query = f"""
            UPDATE {table_name}
            SET R_NO = %s
            WHERE STUDENT_ID = %s
            """
            cursor.execute(update_query, (roll_number, new_row[0]))
            roll_number += 1
        
        db.commit()
        return {"message": "Roll numbers generated successfully"}
    except mysql.connector.Error as err:
        db.rollback()  # Rollback in case of error
        return {"message": "Error inserting data", "error": str(err)}

app.include_router(rl_router)