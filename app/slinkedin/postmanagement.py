from fastapi import FastAPI, APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
import mysql.connector
from db import get_db1
import json

post_router = APIRouter()

class PostData(BaseModel):
    UserId: str
    PostContent: str
    MediaUrl: Optional[List[str]] = Field(default_factory=list)
    Tags: Optional[List[str]] = Field(default_factory=list)
    Collaborations: Optional[List[str]] = Field(default_factory=list)
    Privacy: str
    TimeStamp: str
    Location: Optional[str] = None
    FriendsList: List[str]

class PostIds(BaseModel):
    post_ids: List[int]

@post_router.post("/addpost")
async def add_post(post: PostData, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    
    # Create the post table if it does not exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS post (
        PostId INT AUTO_INCREMENT PRIMARY KEY,
        UserId VARCHAR(255),
        PostContent TEXT,
        MediaUrl JSON,
        Tags JSON,
        Collaborations JSON,
        Privacy VARCHAR(50),
        TimeStamp DATETIME,
        Location VARCHAR(255)
    )
    """
    cursor.execute(create_table_query)
    
    # Convert empty strings to empty lists
    media_url = post.MediaUrl if post.MediaUrl else []
    tags = post.Tags if post.Tags else []
    collaborations = post.Collaborations if post.Collaborations else []
    
    # Insert the post data into the post table
    insert_post_query = """
    INSERT INTO post (UserId, PostContent, MediaUrl, Tags, Collaborations, Privacy, TimeStamp, Location)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_post_query, (
        post.UserId, post.PostContent, json.dumps(media_url), json.dumps(tags),
        json.dumps(collaborations), post.Privacy, post.TimeStamp, post.Location
    ))
    db.commit()
    
    # Get the PostId of the newly inserted post
    post_id = cursor.lastrowid
    
    # Fetch the current posts and posts_count for the user
    cursor.execute("SELECT posts, posts_count FROM slinkedinusers WHERE UserId = %s", (post.UserId,))
    user_data = cursor.fetchone()
    
    if user_data:
        current_posts = json.loads(user_data['posts']) if user_data['posts'] else []
        current_posts_count = user_data['posts_count'] if user_data['posts_count'] else 0
        
        # Update the posts and posts_count
        current_posts.append(post_id)
        new_posts_count = current_posts_count + 1
        
        update_user_query = """
        UPDATE slinkedinusers
        SET posts = %s, posts_count = %s
        WHERE UserId = %s
        """
        cursor.execute(update_user_query, (json.dumps(current_posts), new_posts_count, post.UserId))
        db.commit()

    # Ensure the feed column exists in the slinkedinusers table
    cursor.execute("SHOW COLUMNS FROM slinkedinusers LIKE 'feed'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("ALTER TABLE slinkedinusers ADD COLUMN feed JSON")
        db.commit()

    # Update the feed for the user and their friends
    friends_list = post.FriendsList
    friends_list.append(post.UserId)  # Include the main user in the feed update

    for friend_id in friends_list:
        cursor.execute("SELECT feed FROM slinkedinusers WHERE UserId = %s", (friend_id,))
        friend_data = cursor.fetchone()

        if friend_data:
            current_feed = json.loads(friend_data['feed']) if friend_data['feed'] else []
            current_feed.append(post_id)

            update_feed_query = """
            UPDATE slinkedinusers
            SET feed = %s
            WHERE UserId = %s
            """
            cursor.execute(update_feed_query, (json.dumps(current_feed), friend_id))
            db.commit()

    return {"message": "Post has been successfully delivered", "post_id": post_id}

@post_router.post("/fetchposts")
async def fetch_posts(post_ids: PostIds, db: mysql.connector.connection.MySQLConnection = Depends(get_db1)):
    cursor = db.cursor(dictionary=True)
    posts = []
    # Fetch the posts with the given PostIds
    if not post_ids.post_ids:
        return []
    for i in post_ids.post_ids:
        cursor.execute("SELECT * FROM post WHERE PostId = %s", (i,))
        post = cursor.fetchone()
        if post:
            posts.append(post) 
    print("posts:", posts)
    return posts