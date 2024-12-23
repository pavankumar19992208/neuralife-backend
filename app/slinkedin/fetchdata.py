from fastapi import FastAPI, APIRouter, HTTPException, Depends ,Query
from pydantic import BaseModel
import mysql.connector
from db import get_db1

SLinkedInUserrouter = APIRouter()

class UserData(BaseModel):
    UserId: str
    Name: str
    user_type: str

class UserName(BaseModel):
    UserId: str
    userName: str

class UserIdRequest(BaseModel):
    UserId: str

@SLinkedInUserrouter.get("/search")
def search_users(query: str = Query(...), db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    sql = """
        SELECT UserId, Name, UserName 
        FROM slinkedinusers 
        WHERE UserName LIKE %s OR Name LIKE %s
        LIMIT 10
    """
    cursor.execute(sql, (f"%{query}%", f"%{query}%"))
    result = cursor.fetchall()
    return result

@SLinkedInUserrouter.post("/fetchuser")
async def fetch_user(user: UserData, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # If user doesn't exist, create the table if not exists and insert the user
    create_table_query = """
    CREATE TABLE IF NOT EXISTS slinkedinusers (
        UserId VARCHAR(255) PRIMARY KEY,
        Name VARCHAR(255),
        user_type VARCHAR(50),
        friends_count INT DEFAULT 0,
        friends_list JSON DEFAULT NULL,
        posts JSON DEFAULT NULL,
        posts_count INT DEFAULT 0,
        UserName VARCHAR(255)
    )
    """
    cursor.execute(create_table_query)
    
    # Create indexes on UserId and Name columns if they do not exist
    cursor.execute("SHOW INDEX FROM slinkedinusers WHERE Key_name = 'idx_userid'")
    if cursor.fetchone() is None:
        cursor.execute("CREATE INDEX idx_userid ON slinkedinusers (UserId)")
    
    cursor.execute("SHOW INDEX FROM slinkedinusers WHERE Key_name = 'idx_name'")
    if cursor.fetchone() is None:
        cursor.execute("CREATE INDEX idx_name ON slinkedinusers (Name)")
    
    # Check if the user exists
    cursor.execute("SELECT * FROM slinkedinusers WHERE UserId = %s", (user.UserId,))
    user_row = cursor.fetchone()
    
    if user_row:
        return user_row
    
    insert_user_query = """
    INSERT INTO slinkedinusers (UserId, Name, user_type, friends_count, friends_list, posts, posts_count, UserName)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_user_query, (user.UserId, user.Name, user.user_type, 0, None, None, 0, None))
    db.commit()
    
    # Fetch the newly inserted user
    cursor.execute("SELECT * FROM slinkedinusers WHERE UserId = %s", (user.UserId,))
    new_user_row = cursor.fetchone()
    
    return new_user_row

@SLinkedInUserrouter.post("/updateusername")
async def update_username(user: UserName, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Check if the username already exists
    check_username_query = "SELECT * FROM slinkedinusers WHERE UserName = %s"
    cursor.execute(check_username_query, (user.userName,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        return {"message": "Username already exists"}
    
    # Update the username where UserId matches
    update_user_query = "UPDATE slinkedinusers SET UserName = %s WHERE UserId = %s"
    cursor.execute(update_user_query, (user.userName, user.UserId))
    db.commit()
    
    return {"message": "Username updated successfully"}

@SLinkedInUserrouter.post("/profiledata")
async def profile_data(user_id_request: UserIdRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Fetch the user data with the given UserId
    cursor.execute("SELECT * FROM slinkedinusers WHERE UserId = %s", (user_id_request.UserId,))
    user_row = cursor.fetchone()
    
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_row

