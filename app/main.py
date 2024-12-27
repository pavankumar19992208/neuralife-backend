# filepath: /app/main.py
from fastapi import FastAPI
from app.tea_login import tl_router
from app.roll_no import rl_router
from app.st_login import stl_router
from app.get_studentlist import std_router
from app.upload_marks import upm_router
from app.acreport import acreport_router
from app.homework import homework_router
from app.slinkedin.chatdata import chatdata_router
from app.slinkedin.chats import chat_router
from app.slinkedin.postmanagement import post_router
from app.slinkedin.friendrequesthandling import friend_request_router
from app.slinkedin.fetchdata import SLinkedInUserrouter
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

app.include_router(tl_router)
app.include_router(stl_router)
app.include_router(std_router)
app.include_router(rl_router)
app.include_router(upm_router)
app.include_router(acreport_router)
app.include_router(homework_router)
app.include_router(SLinkedInUserrouter)
app.include_router(post_router)
app.include_router(friend_request_router)
app.include_router(chat_router)
app.include_router(chatdata_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)