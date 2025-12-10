# agent.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from tools import sales_tools
from src.prompts import sales_system_instruction

# 1. Cấu hình
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 2. Khởi tạo Model
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash-lite',
    tools=sales_tools,
    system_instruction=sales_system_instruction
)

# --- BỘ NHỚ RAM (Lưu phiên chat hiện tại) ---
# Dùng Dictionary để lưu các phiên chat đang hoạt động
# Khi tắt server, biến này sẽ mất -> Đúng ý bạn muốn
active_sessions = {}

def get_chat_response(user_message: str, user_id: str = "guest"):
    """
    Hàm xử lý chat:
    - user_id: Mã định danh phiên (Frontend gửi lên).
    """
    if not api_key:
        return "Lỗi hệ thống: Chưa cấu hình API Key."

    global active_sessions

    # 1. Kiểm tra xem user_id này đã có phiên chat chưa
    if user_id not in active_sessions:
        print(f"✨ [RAM] Tạo phiên chat mới cho: {user_id}")
        # Bắt đầu phiên mới với lịch sử rỗng
        active_sessions[user_id] = model.start_chat(
            history=[], 
            enable_automatic_function_calling=True
        )
    
    # 2. Lấy phiên chat ra dùng
    chat_session = active_sessions[user_id]
    
    try:
        # 3. Gửi tin nhắn
        response = chat_session.send_message(user_message)
        return response.text
    except Exception as e:
        # Nếu phiên lỗi (timeout, token quá dài...), xóa đi tạo lại
        print(f"⚠️ Lỗi phiên chat của {user_id}: {e}")
        del active_sessions[user_id]
        return "Xin lỗi, phiên làm việc đã hết hạn hoặc có lỗi. Vui lòng thử lại câu hỏi."