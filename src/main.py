from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent import agent_manager
from .database import db_manager

# Tự động tạo DB khi khởi động
db_manager.initialize_db()

app = FastAPI(title="AI Sales Backend Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    message: str
    user_id: str = "guest"

@app.post("/chat")
async def chat(inp: ChatInput):
    reply = agent_manager.get_response(inp.user_id, inp.message)
    return {"response": reply}