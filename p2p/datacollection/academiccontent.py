from fastapi import FastAPI, APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
from pymongo import MongoClient
import urllib.parse
from bson import ObjectId

academic_router = APIRouter()

# URL-encode the username and password
username = urllib.parse.quote_plus("neuralifecore")
password = urllib.parse.quote_plus("Devtest@123")

# MongoDB Atlas client setup
client = MongoClient(f"mongodb+srv://{username}:{password}@neuralife.a15hb.mongodb.net/?retryWrites=true&w=majority&appName=neuraLife")
db = client["academic_syllabus"]
content_collection = db["academic_content"]
syllabus_collection = db["syllabus_type"]

class MetadataRequest(BaseModel):
    schoolid: str

class AcademicContent(BaseModel):
    syllabustype: str
    schoolid: str
    grade: str
    subject: str
    chapterscount: int
    chapters: List[str]
    exercises: List[str]

def convert_objectid(data):
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

@academic_router.post("/addtitles")
async def add_titles(content: AcademicContent):
    # Create the structure to store in MongoDB
    data = {
        "syllabustype": content.syllabustype,
        "schoolid": content.schoolid,
        "grade": content.grade,
        "subject": content.subject,
        "chaptercount": content.chapterscount,
        "chapters": [
            {"chapter": chapter, "exercises": exercise} for chapter, exercise in zip(content.chapters, content.exercises)
        ]
    }
    
    # Update the data in the academic_content collection
    content_collection.update_one(
        {"syllabustype": content.syllabustype, "schoolid": content.schoolid, "grade": content.grade, "subject": content.subject},
        {"$set": data},
        upsert=True
    )
    
    # Store the syllabustype in the syllabus_type collection
    syllabus_data = {
        "schoolid": content.schoolid,
        "syllabustype": content.syllabustype
    }
    syllabus_collection.update_one(
        {"schoolid": content.schoolid},
        {"$set": syllabus_data},
        upsert=True
    )
    
    return {"message": "Academic content added successfully"}

@academic_router.post("/getmetadata")
async def get_metadata(request: MetadataRequest):
    schoolid = request.schoolid
    
    # Find the syllabustype for the given schoolid
    syllabus_entry = syllabus_collection.find_one({"schoolid": schoolid})
    if not syllabus_entry:
        raise HTTPException(status_code=404, detail="Syllabus type not found for the given schoolid")
    
    syllabustype = syllabus_entry["syllabustype"]
    
    # Find the metadata for the given syllabustype and schoolid
    metadata = content_collection.find({"syllabustype": syllabustype, "schoolid": schoolid})
    print(metadata)
    if not metadata:
        raise HTTPException(status_code=404, detail="Metadata not found for the given syllabustype and schoolid")
    
    # Convert ObjectId to string
    relevant_metadata = convert_objectid(list(metadata))
    
    return relevant_metadata

# Add the router to your main application
app = FastAPI()
app.include_router(academic_router)