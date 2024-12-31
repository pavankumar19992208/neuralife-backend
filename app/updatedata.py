from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from db import get_db1
import mysql.connector

update_router = APIRouter()

class UpdatePasswordRequest(BaseModel):
    UserId: str
    currentPassword: str
    newPassword: str
    usertype: str

@update_router.post("/updatepassword")
async def update_password(request: UpdatePasswordRequest, db=Depends(get_db1)):
    cursor = db.cursor()
    
    if request.usertype == 'student':
        # Check if the current password matches
        cursor.execute("SELECT Password FROM student WHERE UserId = %s", (request.UserId,))
        result = cursor.fetchone()
        if not result or result[0] != request.currentPassword:
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update the password
        cursor.execute("UPDATE student SET Password = %s WHERE UserId = %s", (request.newPassword, request.UserId))
    
    elif request.usertype == 'teacher':
        # Check if the current password matches
        cursor.execute("SELECT password FROM teachers WHERE UserId = %s", (request.UserId,))
        result = cursor.fetchone()
        if not result or result[0] != request.currentPassword:
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update the password
        cursor.execute("UPDATE teachers SET password = %s WHERE UserId = %s", (request.newPassword, request.UserId))
    
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    db.commit()
    return {"message": "Password updated successfully"}