from fastapi import FastAPI, APIRouter
from webpage.sch_registration import sch_router
from webpage.st_registration import st_router
from webpage.sch_login import schl_router
from webpage.tea_registration import tea_router
from app.tea_login import tl_router
from app.roll_no import rl_router
from app.st_login import stl_router
from app.get_studentlist import std_router
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
app.include_router(st_router)
app.include_router(schl_router)
app.include_router(tea_router)
app.include_router(tl_router)
app.include_router(stl_router)
app.include_router(std_router)
app.include_router(rl_router)