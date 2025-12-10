import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Tải key từ file .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("GEMINI_API_KEY")

# Kiểm tra API key
if not api_key or api_key == "your_api_key_here":
    print("❌ GEMINI_API_KEY chưa được cấu hình!")
    print("📌 Hướng dẫn:")
    print("   1. Truy cập: https://aistudio.google.com/apikey")
    print("   2. Sao chép API key")
    print("   3. Mở file .env trong thư mục project")
    print("   4. Thay 'your_api_key_here' bằng API key của bạn")
    print("   5. Lưu file và chạy lại script này")
    exit(1)

# 2. Cấu hình
genai.configure(api_key=api_key)

# 3. Gọi thử model Gemini 2.5 Flash Lite (nhanh và miễn phí)
try:
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    print("Đang gửi tin nhắn tới Gemini...")
    response = model.generate_content("Chào bạn, hãy giới thiệu ngắn gọn về bản thân.")
    
    # 4. In kết quả
    print("✓ Phản hồi từ AI:")
    print(response.text)
except Exception as e:
    print(f"❌ Lỗi: {e}")

#- models/gemini-flash-lite-latest
#- models/gemini-pro-latest
#- models/gemini-2.5-flash-lite
#- models/gemini-2.5-flash-image-preview
#- models/gemini-2.5-flash-image
#- models/gemini-2.5-flash-preview-09-2025
#- models/gemini-2.5-flash-lite-preview-09-2025
#- models/gemini-3-pro-preview
#- models/gemini-3-pro-image-preview
#- models/nano-banana-pro-preview
#- models/gemini-robotics-er-1.5-preview
#- models/gemini-2.5-computer-use-preview-10-2025