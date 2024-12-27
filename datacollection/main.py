# filepath: /datacollection/main.py
from fastapi import FastAPI
from academiccontent import academic_router
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
    return {"Hello": "World"}

app.include_router(academic_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)