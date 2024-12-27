# filepath: /webpage/main.py
from fastapi import FastAPI
from sch_registration import sch_router
from sch_login import schl_router
from tregister import teacher_router
from schooldata import school_data
from classtimetable import ct_router
from StudentRegistration import studentregistration_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(docs_url="/docs")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {" Segment ": " Webpage "}

app.include_router(sch_router)
app.include_router(schl_router)
app.include_router(teacher_router)
app.include_router(school_data)
app.include_router(ct_router)
app.include_router(studentregistration_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)