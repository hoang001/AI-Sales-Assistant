"""
Test script để kiểm tra logic chạy của project
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent import agent_manager
from src.database import db_manager

# 1. Khởi tạo database
print("\n" + "="*60)
print("📍 BƯỚC 1: Khởi tạo Database")
print("="*60)
db_manager.initialize_db()
print("✅ Database initialized")

# 2. Test Agent Response
print("\n" + "="*60)
print("📍 BƯỚC 2: Test Agent Response")
print("="*60)
test_message = "Tôi muốn tìm laptop gaming giá dưới 20 triệu"
print(f"👤 User: {test_message}")
print("-" * 60)

try:
    response = agent_manager.get_response("test_user", test_message)
    print(f"🤖 AI Response:\n{response}")
    print("-" * 60)
    print("✅ Agent hoạt động bình thường")
except Exception as e:
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✨ TEST HOÀN THÀNH")
print("="*60)
