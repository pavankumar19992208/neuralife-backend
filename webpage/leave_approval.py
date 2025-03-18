from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from datetime import date, datetime
import logging
import boto3
from db import get_db1
import os
from dotenv import load_dotenv

load_dotenv()

leave_approval_router = APIRouter()

# Configure Logging
logging.basicConfig(level=logging.INFO)

# AWS SNS Client
sns_client = boto3.client(
    "sns",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="eu-north-1"
)

# Create Leave Table if Not Exists
def create_leave_table(db):
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_leaves (
            leave_id INT AUTO_INCREMENT PRIMARY KEY,
            teacherid INT,
            status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            reason TEXT NOT NULL,
            requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_by VARCHAR(255),
            approved_at TIMESTAMP NULL,
            leaves_count INT DEFAULT 0,
            FOREIGN KEY (teacherid) REFERENCES teachers(teacherid) ON DELETE CASCADE
        )
    """)
    db.commit()

# Pydantic Models
class LeaveRequest(BaseModel):
    teacherid: int
    start_date: date
    end_date: date
    reason: str

class LeaveApproval(BaseModel):
    leave_id: int
    approved_by: str
    status: str  # 'Approved' or 'Rejected'

# Send SMS Notification via AWS SNS
def send_sms(phone_number: str, message: str):
    try:
        # Ensure the phone number includes the country code
        if not phone_number.startswith("+"):
            phone_number = "+91" + phone_number  # Assuming +91 for India
        logging.info(f"Sending SMS to {phone_number}")
        response = sns_client.publish(
            PhoneNumber=phone_number,
            Message=message
        )
        logging.info(f"SMS sent successfully: {response}")
    except Exception as e:
        logging.error(f"Failed to send SMS: {e}")

# Request Leave
@leave_approval_router.post("/request-leave/")
async def request_leave(request: LeaveRequest, db=Depends(get_db1)):
    create_leave_table(db)
    cursor = db.cursor()
    insert_query = """
    INSERT INTO teacher_leaves (teacherid, start_date, end_date, reason, leaves_count)
    VALUES (%s, %s, %s, %s, %s)
    """
    leaves_count = (request.end_date - request.start_date).days + 1
    cursor.execute(insert_query, (request.teacherid, request.start_date, request.end_date, request.reason, leaves_count))
    db.commit()
    return {"message": "Leave request submitted"}

# Approve/Reject Leave with SMS Notification
@leave_approval_router.put("/update-leave-status")
async def update_leave_status(approval: LeaveApproval, db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    try:
        # Fetch leave request
        cursor.execute("SELECT teacherid, start_date, end_date FROM teacher_leaves WHERE leave_id = %s", (approval.leave_id,))
        leave_request = cursor.fetchone()
        
        if not leave_request:
            raise HTTPException(status_code=404, detail="Leave request not found")

        teacher_id = leave_request["teacherid"]
        start_date = leave_request["start_date"]
        end_date = leave_request["end_date"]

        # Fetch Teacher Contact Number
        cursor.execute("SELECT contactNumber, Name FROM teachers WHERE teacherid = %s", (teacher_id,))
        teacher_data = cursor.fetchone()

        if not teacher_data:
            raise HTTPException(status_code=404, detail="Teacher not found")

        phone_number = teacher_data["contactNumber"]
        teacher_name = teacher_data["Name"]

        # Update Leave Status
        update_query = """
        UPDATE teacher_leaves 
        SET status = %s, approved_by = %s, approved_at = NOW()
        WHERE leave_id = %s
        """
        cursor.execute(update_query, (approval.status, approval.approved_by, approval.leave_id))

        # Update Leave Count if Approved
        if approval.status == "Approved":
            cursor.execute("""
                UPDATE teacher_leaves
                SET leaves_count = COALESCE(leaves_count, 0) + 1
                WHERE teacherid = %s
            """, (teacher_id,))

        db.commit()

        # Send SMS Notification
        leave_duration = (end_date - start_date).days + 1
        message = f"Dear {teacher_name}, your leave request for {leave_duration} days has been {approval.status.lower()} by {approval.approved_by}.\n neuraLife"
        send_sms(phone_number, message)

        return {"message": f"Leave {approval.status.lower()} successfully"}
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating leave status: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# Get Pending Leave Requests
@leave_approval_router.get("/pending-leaves", response_model=List[dict])
async def get_pending_leaves(db=Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT tl.leave_id, tl.teacherid, t.Name as teacher_name, tl.reason, tl.start_date, tl.end_date, tl.requested_date, tl.leaves_count, tl.status
        FROM teacher_leaves tl
        JOIN teachers t ON tl.teacherid = t.teacherid
        WHERE tl.status = 'Pending'
        ORDER BY tl.requested_date DESC
    """)
    leaves = cursor.fetchall()
    return leaves