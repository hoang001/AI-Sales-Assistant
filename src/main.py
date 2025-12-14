from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import sys
import json # <--- Thêm import này

# Đảm bảo đường dẫn import đúng
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .agent import agent_manager
from .database import db_manager
from .services import store_service # <--- QUAN TRỌNG: Import service tìm cửa hàng

# Khởi tạo DB
db_manager.initialize_db()

app = FastAPI(title="AI Sales Assistant")

# --- CẤU HÌNH CORS (Để Ngrok và Vercel kết nối được) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép tất cả các nguồn (bao gồm Ngrok)
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. MOUNT THƯ MỤC STATIC ---
static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# --- 2. API CHAT ---
class ChatInput(BaseModel):
    message: str
    user_id: str = "guest"

@app.post("/chat")
async def chat(inp: ChatInput):
    message = inp.message.strip()
    user_id = inp.user_id

    print(f"📩 Nhận tin nhắn: {message}") # Log để debug

    # ===============================
    # CASE 1: XỬ LÝ GPS TỪ FRONTEND
    # (Frontend gửi dạng: "GPS:21.033,105.84")
    # ===============================
    if message.startswith("GPS:"):
        # Gọi hàm tìm cửa hàng trong services.py (đã tích hợp Google Maps/SerpApi)
        reply = store_service.find_stores(message)
        return {"response": reply}

    # ===============================
    # CASE 2: CHAT BÌNH THƯỜNG (AI)
    # ===============================
    try:
        reply = agent_manager.get_response(user_id, message)
        return {"response": reply}
    except Exception as e:
        print(f"❌ Lỗi AI: {e}")
        return {"response": "Xin lỗi, hệ thống đang bận. Bạn thử lại sau nhé!"}


# --- 3. TRANG CHỦ ---
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_path, "index.html"))