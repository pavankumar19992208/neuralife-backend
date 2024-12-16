from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
import mysql.connector
from db import get_db1
import json

friend_request_router = APIRouter()

class FriendRequest(BaseModel):
    UserId: str
    FriendId: str

class UserIdRequest(BaseModel):
    UserId: str

@friend_request_router.post("/friendrequests")
async def friend_requests(request: FriendRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Create the friendrequests table if it does not exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS friendrequests (
        id INT AUTO_INCREMENT PRIMARY KEY,
        UserId VARCHAR(255),
        FriendId VARCHAR(255),
        status VARCHAR(50) DEFAULT NULL
    )
    """
    cursor.execute(create_table_query)
    
    # Insert the friend request into the friendrequests table
    insert_request_query = """
    INSERT INTO friendrequests (UserId, FriendId, status)
    VALUES (%s, %s, NULL)
    """
    cursor.execute(insert_request_query, (request.UserId, request.FriendId))
    db.commit()
    
    return {"message": "Friend request sent successfully"}

@friend_request_router.post("/fetchfriendrequests")
async def fetch_friend_requests(user_id_request: UserIdRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    print(user_id_request.UserId)
    # Fetch the friend requests with the given UserId and status is NULL
    cursor.execute("SELECT UserId FROM friendrequests WHERE FriendId = %s AND status IS NULL", (user_id_request.UserId,))
    friend_ids = cursor.fetchall()
    print(friend_ids)
    if not friend_ids:
        return []
    
    friend_profiles = []
    for friend_id in friend_ids:
        cursor.execute("SELECT * FROM slinkedinusers WHERE UserId = %s", (friend_id['UserId'],))
        friend_profile = cursor.fetchone()
        if friend_profile:
            friend_profiles.append(friend_profile)
    print(friend_profiles)
    return friend_profiles

@friend_request_router.post("/addfriend")
async def add_friend(request: FriendRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Fetch the current friends_list and friends_count for the user
    cursor.execute("SELECT friends_list, friends_count FROM slinkedinusers WHERE UserId = %s", (request.UserId,))
    user_data = cursor.fetchone()
    if user_data:
        current_friends = json.loads(user_data['friends_list']) if user_data['friends_list'] else []
        current_friends.append(request.FriendId)
        new_friends_count = user_data['friends_count'] + 1
        update_user_query = "UPDATE slinkedinusers SET friends_list = %s, friends_count = %s WHERE UserId = %s"
        cursor.execute(update_user_query, (json.dumps(current_friends), new_friends_count, request.UserId))
    
    # Fetch the current friends_list and friends_count for the friend
    cursor.execute("SELECT friends_list, friends_count FROM slinkedinusers WHERE UserId = %s", (request.FriendId,))
    friend_data = cursor.fetchone()
    if friend_data:
        current_friends = json.loads(friend_data['friends_list']) if friend_data['friends_list'] else []
        current_friends.append(request.UserId)
        new_friends_count = friend_data['friends_count'] + 1
        update_friend_query = "UPDATE slinkedinusers SET friends_list = %s, friends_count = %s WHERE UserId = %s"
        cursor.execute(update_friend_query, (json.dumps(current_friends), new_friends_count, request.FriendId))
    
    # Update the status of the friend request to Accepted
    update_request_query = "UPDATE friendrequests SET status = 'Accepted' WHERE UserId = %s AND FriendId = %s"
    cursor.execute(update_request_query, (request.UserId, request.FriendId))
    db.commit()
    
    return {"message": "Friend request accepted"}

@friend_request_router.post("/reject")
async def reject_friend_request(request: FriendRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Delete the friend request from the friendrequests table
    delete_request_query = "DELETE FROM friendrequests WHERE UserId = %s AND FriendId = %s"
    cursor.execute(delete_request_query, (request.UserId, request.FriendId))
    db.commit()
    
    return {"message": "Friend request rejected"}

# Add the router to your main application
app = FastAPI()
app.include_router(friend_request_router)