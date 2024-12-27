# filepath: /webpage/main.py
from fastapi import FastAPI
from webpage.sch_registration import sch_router
from webpage.sch_login import schl_router
from webpage.tregister import teacher_router
from webpage.schooldata import school_data
from webpage.classtimetable import ct_router
from webpage.StudentRegistration import studentregistration_router
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(teacher_router)
app.include_router(school_data)
app.include_router(ct_router)
app.include_router(studentregistration_router)