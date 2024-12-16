from fastapi import FastAPI, APIRouter, HTTPException, Depends
from pydantic import BaseModel
import mysql.connector
from db import get_db1
import json
from datetime import datetime

chat_router = APIRouter()

class CreateChatRequest(BaseModel):
    UserId1: str
    UserId2: str

class AddMessageRequest(BaseModel):
    ChatId: int
    SenderId: str
    Content: str
    MessageType: str

@chat_router.post("/createchat")
async def create_chat(request: CreateChatRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Create the Chats table if it does not exist
    create_chats_table_query = """
    CREATE TABLE IF NOT EXISTS Chats (
        id INT AUTO_INCREMENT PRIMARY KEY,
        UserId1 VARCHAR(255),
        UserId2 VARCHAR(255),
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_chats_table_query)
    
    # Insert the chat into the Chats table
    insert_chat_query = """
    INSERT INTO Chats (UserId1, UserId2)
    VALUES (%s, %s)
    """
    cursor.execute(insert_chat_query, (request.UserId1, request.UserId2))
    db.commit()
    
    # Get the ChatId of the newly inserted chat
    chat_id = cursor.lastrowid
    
    # Create the chats column in slinkedinusers table if it does not exist
    cursor.execute("SHOW COLUMNS FROM slinkedinusers LIKE 'chats'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE slinkedinusers ADD COLUMN chats JSON DEFAULT NULL")
    
    # Update the chats column for UserId1
    cursor.execute("SELECT chats FROM slinkedinusers WHERE UserId = %s", (request.UserId1,))
    user1_data = cursor.fetchone()
    if user1_data:
        current_chats = json.loads(user1_data['chats']) if user1_data['chats'] else []
        current_chats.append(chat_id)
        update_user1_query = "UPDATE slinkedinusers SET chats = %s WHERE UserId = %s"
        cursor.execute(update_user1_query, (json.dumps(current_chats), request.UserId1))
    
    # Update the chats column for UserId2
    cursor.execute("SELECT chats FROM slinkedinusers WHERE UserId = %s", (request.UserId2,))
    user2_data = cursor.fetchone()
    if user2_data:
        current_chats = json.loads(user2_data['chats']) if user2_data['chats'] else []
        current_chats.append(chat_id)
        update_user2_query = "UPDATE slinkedinusers SET chats = %s WHERE UserId = %s"
        cursor.execute(update_user2_query, (json.dumps(current_chats), request.UserId2))
    
    db.commit()
    
    return {"message": "Chat created successfully", "ChatId": chat_id}

@chat_router.post("/addmessage")
async def add_message(request: AddMessageRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Create the messages table if it does not exist
    create_messages_table_query = """
    CREATE TABLE IF NOT EXISTS Messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ChatId INT,
        SenderId VARCHAR(255),
        Content TEXT,
        MessageType ENUM('text', 'image', 'file'),
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        Is_Read BOOLEAN DEFAULT FALSE
    )
    """
    cursor.execute(create_messages_table_query)
    
    # Insert the message into the Messages table
    insert_message_query = """
    INSERT INTO Messages (ChatId, SenderId, Content, MessageType, CreatedAt, Is_Read)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_message_query, (
        request.ChatId, request.SenderId, request.Content, request.MessageType, datetime.now(), False
    ))
    db.commit()
    
    return {"message": "Message added successfully"}
