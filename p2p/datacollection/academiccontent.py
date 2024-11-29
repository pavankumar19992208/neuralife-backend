from fastapi import FastAPI, APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
import urllib.parse

academic_router = APIRouter()

# URL-encode the username and password
username = urllib.parse.quote_plus("neuralifecore")
password = urllib.parse.quote_plus("Devtest@123")

# MongoDB Atlas client setup
client = MongoClient(f"mongodb+srv://{username}:{password}@neuralife.a15hb.mongodb.net/?retryWrites=true&w=majority&appName=neuraLife")
db = client["academic_syllabus"]
collection = db["academic_content"]

class AcademicContent(BaseModel):
    syllabustype: str
    schoolid: str
    grade: str
    subject: str
    chapterscount: int
    chapters: List[str]
    exercises: List[str]

@academic_router.post("/addtitles")
async def add_titles(content: AcademicContent):
    # Create the structure to store in MongoDB
    data = {
        content.syllabustype: {
            content.schoolid: {
                content.grade: {
                    content.subject: {
                        "chaptercount": content.chapterscount,
                        "chapters": {
                            chapter: {"exercise": exercise} for chapter, exercise in zip(content.chapters, content.exercises)
                        }
                    }
                }
            }
        }
    }
    
    # Insert the data into the MongoDB collection
    collection.insert_one(data)
    
    return {"message": "Academic content added successfully"}

# Add the router to your main application
app = FastAPI()
app.include_router(academic_router)