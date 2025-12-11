import google.generativeai as genai
from .config import settings
from .tools import defined_tools
from .prompts import sales_system_instruction

class AgentManager:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        model_name = 'gemini-2.5-flash-lite' 
        
        print(f"🤖 Đang khởi tạo AI Model: {model_name}...")
        self.model = genai.GenerativeModel(
            model_name=model_name,
            tools=defined_tools,
            system_instruction=sales_system_instruction
        )
        self.sessions = {}

    def get_response(self, user_id: str, message: str):
        # Tạo session mới nếu chưa có
        if user_id not in self.sessions:
            print(f"✨ New Session: {user_id}")
            self.sessions[user_id] = self.model.start_chat(history=[], enable_automatic_function_calling=True)
        
        try:
            # Gửi tin nhắn cho AI
            response = self.sessions[user_id].send_message(message)
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ LỖI NGHIÊM TRỌNG TẠI AGENT: {error_msg}\n")
            
            # Xóa session bị lỗi để lần sau khách chat sẽ tạo session mới sạch sẽ
            if user_id in self.sessions:
                del self.sessions[user_id]
            
            # Trả về thông báo lỗi cụ thể để debug trên Swagger/Frontend
            # (Sau này chạy thật thì có thể sửa lại câu xin lỗi sau)
            return f"⚠️ Lỗi hệ thống: {error_msg}"

agent_manager = AgentManager()