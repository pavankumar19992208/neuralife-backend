# filepath: /datacollection/main.py
from fastapi import FastAPI
from datacollection.academiccontent import academic_router
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
app.include_router(academic_router)