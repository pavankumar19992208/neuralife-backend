# filepath: /app/main.py
from fastapi import FastAPI
from tea_login import tl_router
from roll_no import rl_router
from st_login import stl_router
from get_studentlist import std_router
from upload_marks import upm_router
from acreport import acreport_router
from homework import homework_router
from slinkedin.chatdata import chatdata_router
from slinkedin.chats import chat_router
from slinkedin.postmanagement import post_router
from slinkedin.friendrequesthandling import friend_request_router
from slinkedin.fetchdata import SLinkedInUserrouter
from fastapi.middleware.cors import CORSMiddleware
from updatedata import update_router

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
    return {" segment ": " Mobile Application "}

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
app.include_router(update_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)