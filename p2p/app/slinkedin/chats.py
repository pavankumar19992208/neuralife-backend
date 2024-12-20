from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
import mysql.connector
from db import get_db1
import json
from datetime import datetime
from typing import List

app = FastAPI()
chat_router = APIRouter()

class CreateChatRequest(BaseModel):
    UserId1: str
    UserId2: str

class AddMessageRequest(BaseModel):
    ChatId: int
    SenderId: str
    Content: str
    MessageType: str

class GetMessagesRequest(BaseModel):
    ChatId: int

class CreateCircleRequest(BaseModel):
    CircleName: str
    CreatedBy: str
    Users: List[str]
    CreatedAt: datetime
    Description: str

class GetCirclesRequest(BaseModel):
    ChatIds: List[str]

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

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
        if not any(chat['ChatId'] == chat_id for chat in current_chats):
            current_chats.append({"ChatId": chat_id, "FriendId": request.UserId2})
        update_user1_query = "UPDATE slinkedinusers SET chats = %s WHERE UserId = %s"
        cursor.execute(update_user1_query, (json.dumps(current_chats), request.UserId1))
    
    # Update the chats column for UserId2
    cursor.execute("SELECT chats FROM slinkedinusers WHERE UserId = %s", (request.UserId2,))
    user2_data = cursor.fetchone()
    if user2_data:
        current_chats = json.loads(user2_data['chats']) if user2_data['chats'] else []
        if not any(chat['ChatId'] == chat_id for chat in current_chats):
            current_chats.append({"ChatId": chat_id, "FriendId": request.UserId1})
        update_user2_query = "UPDATE slinkedinusers SET chats = %s WHERE UserId = %s"
        cursor.execute(update_user2_query, (json.dumps(current_chats), request.UserId2))
    
    db.commit()
    
    return {"ChatId": chat_id}

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

@chat_router.post("/getmessages")
async def get_messages(request: GetMessagesRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Fetch messages from the Messages table based on ChatId
    cursor.execute("SELECT * FROM Messages WHERE ChatId = %s ORDER BY CreatedAt ASC", (request.ChatId,))
    messages = cursor.fetchall()
    
    return messages

@chat_router.post("/createcircle")
async def create_circle(request: CreateCircleRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Create the Circles table if it does not exist
    create_circles_table_query = """
    CREATE TABLE IF NOT EXISTS Circles (
        id INT AUTO_INCREMENT PRIMARY KEY,
        CircleName VARCHAR(255),
        CreatedBy VARCHAR(255),
        Users JSON,
        CreatedAt TIMESTAMP,
        Description TEXT,
        ChatId VARCHAR(255)
    )
    """
    cursor.execute(create_circles_table_query)
    
    # Insert the circle into the Circles table
    insert_circle_query = """
    INSERT INTO Circles (CircleName, CreatedBy, Users, CreatedAt, Description, ChatId)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_circle_query, (
        request.CircleName, request.CreatedBy, json.dumps(request.Users), request.CreatedAt, request.Description, None
    ))
    circle_id = cursor.lastrowid
    chat_id = f"ci{circle_id}"
    cursor.execute("UPDATE Circles SET ChatId = %s WHERE id = %s", (chat_id, circle_id))
    db.commit()
    
    # Create the circles column in slinkedinusers table if it does not exist
    cursor.execute("SHOW COLUMNS FROM slinkedinusers LIKE 'circles'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE slinkedinusers ADD COLUMN circles JSON DEFAULT NULL")
    
    # Update the circles column for each user in the list
    for user_id in request.Users:
        cursor.execute("SELECT circles FROM slinkedinusers WHERE UserId = %s", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            current_circles = json.loads(user_data['circles']) if user_data['circles'] else []
            if not any(circle['ChatId'] == chat_id for circle in current_circles):
                current_circles.append({"ChatId": chat_id, "CircleName": request.CircleName})
            update_user_query = "UPDATE slinkedinusers SET circles = %s WHERE UserId = %s"
            cursor.execute(update_user_query, (json.dumps(current_circles), user_id))
    
    db.commit()
    
    return {"ChatId": chat_id}

@chat_router.post("/getcircles")
async def get_circles(request: GetCirclesRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Fetch circles from the Circles table based on ChatIds
    format_strings = ','.join(['%s'] * len(request.ChatIds))
    cursor.execute(f"SELECT * FROM Circles WHERE ChatId IN ({format_strings})", tuple(request.ChatIds))
    circles = cursor.fetchall()
    
    if not circles:
        return ""
    
    return circles

@chat_router.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Chat {chat_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Chat {chat_id}: Client disconnected")

# Add the router to your main application
app.include_router(chat_router)