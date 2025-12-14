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

    print(f"📩 Nhận tin nhắn: {message}")

    # ===============================
    # 🎯 TRƯỜNG HỢP 1: XỬ LÝ ĐỊNH VỊ GPS (Nút bấm trên Frontend)
    # ===============================
    if message.startswith("GPS:"):
        try:
            # Tách lấy tọa độ từ chuỗi "GPS:21.02,105.83"
            _, coords = message.split(":")
            lat, lng = coords.split(",")
            
            # Gọi hàm find_nearest_store trong services.py (Dùng SerpApi)
            # Hàm này bạn đã có trong file services.py cũ
            reply = store_service.find_nearest_store(float(lat), float(lng))
            
            return {"response": reply}
            
        except Exception as e:
            print(f"❌ Lỗi GPS: {e}")
            return {"response": "⚠️ Xin lỗi, không thể xác định vị trí của bạn lúc này."}

    # ===============================
    # 🤖 TRƯỜNG HỢP 2: CHAT VỚI AI (Các câu hỏi thường)
    # ===============================
    # Nếu khách hỏi "Tìm cửa hàng ở Cầu Giấy" -> AI sẽ tự gọi tool find_stores (tìm theo tên)
    try:
        reply = agent_manager.get_response(user_id, message)
        return {"response": reply}
    except Exception as e:
        print(f"❌ Lỗi AI: {e}")
        return {"response": "Hệ thống đang bận, vui lòng thử lại sau."}

# --- 3. TRANG CHỦ ---
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_path, "index.html"))