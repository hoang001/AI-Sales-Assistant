import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Tải key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "your_api_key_here":
    print("❌ GEMINI_API_KEY chưa được cấu hình!")
    print("📌 Hướng dẫn:")
    print("   1. Truy cập: https://aistudio.google.com/apikey")
    print("   2. Sao chép API key")
    print("   3. Mở file .env trong thư mục project")
    print("   4. Thay 'your_api_key_here' bằng API key của bạn")
    print("   5. Lưu file và chạy lại script này")
    exit(1)

genai.configure(api_key=api_key)

# 2. Liệt kê các model
print("Danh sách các model bạn có thể dùng:")
try:
    for m in genai.list_models():
        # Chỉ hiện các model có khả năng tạo nội dung (chat)
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"❌ Lỗi: {e}")
    print("   Kiểm tra lại API key trong file .env")