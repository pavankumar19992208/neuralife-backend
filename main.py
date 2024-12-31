from fastapi import FastAPI, APIRouter
from webpage.sch_registration import sch_router
from webpage.sch_login import schl_router
from app.tea_login import tl_router
from app.roll_no import rl_router
from app.st_login import stl_router
from app.get_studentlist import std_router
from app.upload_marks import upm_router
from app.acreport import acreport_router
from webpage.tregister import teacher_router
from app.homework import homework_router
from app.slinkedin.chatdata import chatdata_router
from app.slinkedin.chats import chat_router
from app.slinkedin.postmanagement import post_router
from datacollection.academiccontent import academic_router
from fastapi.middleware.cors import CORSMiddleware
from webpage.schooldata import school_data
from app.slinkedin.friendrequesthandling import friend_request_router
from webpage.classtimetable import ct_router
from webpage.StudentRegistration import studentregistration_router
from app.slinkedin.fetchdata import SLinkedInUserrouter
from app.updatedata import update_router
app = FastAPI(docs_url="/docs")

origins = [
    "*",  # Allow all origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Your routes go here
app.include_router(sch_router)
app.include_router(schl_router)
app.include_router(tl_router)
app.include_router(stl_router)
app.include_router(std_router)
app.include_router(rl_router)
app.include_router(upm_router)
app.include_router(acreport_router)
app.include_router(studentregistration_router)
app.include_router(homework_router)
app.include_router(school_data)
app.include_router(teacher_router)
app.include_router(ct_router)
app.include_router(academic_router)
app.include_router(SLinkedInUserrouter)
app.include_router(post_router)
app.include_router(friend_request_router)
app.include_router(chat_router)
app.include_router(chatdata_router)
app.include_router(update_router)