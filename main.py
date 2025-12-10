# main.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Import các thành phần bạn đã xây dựng
from src.prompts import sales_system_instruction
from tools import sales_tools

# 1. Cấu hình
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 2. Khởi tạo Agent
# Dùng gemini-2.5-flash-lite cho nhanh và tiết kiệm quota
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash-lite', 
    tools=sales_tools,
    system_instruction=sales_system_instruction
)

# 3. Bắt đầu hội thoại (bật chế độ tự động gọi tool)
chat = model.start_chat(enable_automatic_function_calling=True)

print("--- AI SALES ASSISTANT (Gõ 'quit' để thoát) ---")

# 4. Vòng lặp Chat
while True:
    user_input = input("\nKhách hàng: ")
    if user_input.lower() in ['quit', 'exit']:
        break
    
    try:
        # Gửi tin nhắn cho AI
        response = chat.send_message(user_input)
        
        # In câu trả lời (nếu có text)
        if response.text:
            print(f"AI: {response.text}")
        else:
            print("AI: (Đang xử lý tác vụ...)")
            
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")