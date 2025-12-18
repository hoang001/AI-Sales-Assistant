from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import sys
import requests
import urllib.parse
import asyncio

# Đảm bảo đường dẫn import đúng
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .agent import agent_manager
from .database import db_manager
from .services import store_service

# ===============================
# KHỞI TẠO
# ===============================
db_manager.initialize_db()

app = FastAPI(title="AI Sales Assistant API")

# ===============================
# CORS (Cấu hình mở rộng để tránh lỗi kết nối)
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả (Vercel, Localhost, Ngrok)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# SCHEMA
# ===============================
class ChatInput(BaseModel):
    message: str
    user_id: str = "guest"

# ===============================
# API CHAT (CÓ STREAMING)
# ===============================
@app.post("/chat")
async def chat(inp: ChatInput):
    message = inp.message.strip()
    user_id = inp.user_id
    print(f"[CHAT] {user_id}: {message}")

    # --- HÀM GENERATOR ĐỂ STREAM DỮ LIỆU ---
    async def response_stream():
        try:
            # 1. ƯU TIÊN: XỬ LÝ GPS (Nút bấm)
            if message.startswith("GPS:"):
                try:
                    _, coords = message.split(":")
                    lat, lng = coords.split(",")
                    # Tìm cửa hàng và trả về ngay (không cần cắt nhỏ)
                    reply = store_service.find_nearest_store(float(lat), float(lng))
                    yield reply
                    return
                except Exception as e:
                    yield "Lỗi xử lý định vị GPS."
                    return

            # 2. ƯU TIÊN: XỬ LÝ TÌM ĐỊA ĐIỂM (Nhập tay)
            location_keywords = [
                "tìm cửa hàng", "cửa hàng gần", "shop gần", "chi nhánh", 
                "địa chỉ cửa hàng", "ở đâu", "gần đây không"
            ]
            
            if any(keyword in message.lower() for keyword in location_keywords):
                # Gọi hàm tìm kiếm địa điểm
                reply = store_service.find_stores_by_text(message)
                yield reply
                return

            # 3. CÒN LẠI: CHAT VỚI AI (Tư vấn sản phẩm)
            # Giả lập hiệu ứng gõ máy (Streaming) cho câu trả lời của AI
            full_response = agent_manager.get_response(user_id, message)
            
            # Cắt nhỏ câu trả lời và gửi từ từ
            chunk_size = 10  # Số ký tự mỗi lần gửi
            for i in range(0, len(full_response), chunk_size):
                chunk = full_response[i:i + chunk_size]
                yield chunk
                await asyncio.sleep(0.01) # Nghỉ 10ms để tạo hiệu ứng mượt

        except Exception as e:
            print(f"[STREAM ERROR] {e}")
            yield f"⚠️ Lỗi hệ thống: {str(e)}"

    # Trả về dữ liệu dạng dòng chảy (Stream)
    return StreamingResponse(response_stream(), media_type="text/plain")

# ===============================
# PROXY IMAGE
# ===============================
@app.get("/proxy-image")
async def proxy_image(url: str = Query(..., description="URL ảnh cần proxy")):
    try:
        decoded_url = urllib.parse.unquote(url)
        # Fake User-Agent để tránh bị chặn bởi một số server ảnh
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(decoded_url, headers=headers, timeout=10, stream=True)
        
        if response.status_code != 200: 
            raise HTTPException(status_code=400)
            
        return StreamingResponse(
            response.iter_content(chunk_size=8192),
            media_type=response.headers.get("content-type", "image/jpeg"),
            headers={"Cache-Control": "public, max-age=3600", "Access-Control-Allow-Origin": "*"}
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Lỗi tải ảnh")

# ===============================
# STATIC FILES (MOUNT CUỐI CÙNG)
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount các thư mục con cụ thể
app.mount("/css", StaticFiles(directory=os.path.join(STATIC_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(STATIC_DIR, "js")), name="js")
# Mount root (Luôn để cuối cùng để không chặn API)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="site")