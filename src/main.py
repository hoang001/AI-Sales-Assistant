from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import sys
import requests
import urllib.parse

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
# CORS (CHO VERCEL / NGROK)
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Khi lên prod có thể giới hạn domain Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ===============================
# SCHEMA
# ===============================
class ChatInput(BaseModel):
    message: str
    user_id: str = "guest"

# ===============================
# API CHAT
# ===============================
@app.post("/chat")
async def chat(inp: ChatInput):
    message = inp.message.strip()
    user_id = inp.user_id

    print(f"[CHAT] {user_id}: {message}")

    # ---- GPS ----
    if message.startswith("GPS:"):
        try:
            _, coords = message.split(":")
            lat, lng = coords.split(",")

            reply = store_service.find_nearest_store(
                float(lat),
                float(lng)
            )
            return {"response": reply}

        except Exception as e:
            print(f"[GPS ERROR] {e}")
            return {
                "response": "Xin lỗi, không thể xác định vị trí của bạn lúc này."
            }

    # ---- AI CHAT ----
    try:
        reply = agent_manager.get_response(user_id, message)
        return {"response": reply}

    except Exception as e:
        print(f"[AI ERROR] {e}")
        return {
            "response": "Hệ thống đang bận, vui lòng thử lại sau."
        }

# ===============================
# PROXY IMAGE (HTTPS SAFE)
# ===============================
@app.get("/proxy-image")
async def proxy_image(
    url: str = Query(..., description="URL ảnh cần proxy")
):
    try:
        decoded_url = urllib.parse.unquote(url)
        parsed_url = urllib.parse.urlparse(decoded_url)

        if not parsed_url.scheme or not parsed_url.netloc:
            raise HTTPException(status_code=400, detail="URL không hợp lệ")

        response = requests.get(
            decoded_url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=10,
            stream=True
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Không thể tải ảnh"
            )

        return StreamingResponse(
            response.iter_content(chunk_size=8192),
            media_type=response.headers.get(
                "content-type", "image/jpeg"
            ),
            headers={
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*"
            }
        )

    except requests.exceptions.RequestException as e:
        print(f"[PROXY REQUEST ERROR] {e}")
        raise HTTPException(status_code=500, detail="Lỗi tải ảnh")

    except Exception as e:
        print(f"[PROXY ERROR] {e}")
        raise HTTPException(status_code=500, detail="Lỗi xử lý ảnh")
