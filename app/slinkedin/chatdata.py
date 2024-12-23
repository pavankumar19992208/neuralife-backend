from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
import mysql.connector
from db import get_db1
import json
from datetime import datetime

chatdata_router = APIRouter()

class UserIdRequest(BaseModel):
    UserId: str

class ChatData(BaseModel):
    ChatId: int
    FriendId: str

@chatdata_router.post("/getchats")
async def get_chats(user_id_request: UserIdRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Fetch the user's chat data
    cursor.execute("SELECT chats FROM slinkedinusers WHERE UserId = %s", (user_id_request.UserId,))
    user_data = cursor.fetchone()
    
    if not user_data or not user_data['chats']:
        return []
    
    chats = json.loads(user_data['chats'])
    chat_details = []
    
    # Check if the photo column exists
    cursor.execute("SHOW COLUMNS FROM slinkedinusers LIKE 'photo'")
    photo_column_exists = cursor.fetchone() is not None
    
    for chat in chats:
        chat_id = chat['ChatId']
        friend_id = chat['FriendId']
        
        # Fetch friend's profile data
        if photo_column_exists:
            cursor.execute("SELECT UserId, UserName, Name, photo FROM slinkedinusers WHERE UserId = %s", (friend_id,))
        else:
            cursor.execute("SELECT UserId, UserName, Name FROM slinkedinusers WHERE UserId = %s", (friend_id,))
        
        friend_profile = cursor.fetchone()
        
        if not friend_profile:
            continue
        
        if not photo_column_exists:
            friend_profile['photo'] = ''
        
        # Fetch the latest message and time
        cursor.execute("SELECT Content, CreatedAt FROM Messages WHERE ChatId = %s ORDER BY CreatedAt DESC LIMIT 1", (chat_id,))
        latest_message = cursor.fetchone()
        
        chat_details.append({
            "ChatId": chat_id,
            "FriendProfile": friend_profile,
            "LatestMessage": latest_message['Content'] if latest_message else '',
            "MessageTime": latest_message['CreatedAt'] if latest_message else ''
        })
    
    return chat_details

