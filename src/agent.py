import google.generativeai as genai
from .config import settings
from .tools import defined_tools
from .prompts import sales_system_instruction

class AgentManager:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash-lite',
            tools=defined_tools,
            # Dùng prompt dài từ file prompts.py
            system_instruction=sales_system_instruction 
        )
        # Bộ nhớ RAM (Session)
        self.sessions = {}

    def get_response(self, user_id: str, message: str):
        if user_id not in self.sessions:
            self.sessions[user_id] = self.model.start_chat(history=[], enable_automatic_function_calling=True)
        
        try:
            chat = self.sessions[user_id]
            response = chat.send_message(message)
            return response.text
        except Exception as e:
            print(f"Lỗi session {user_id}: {e}")
            del self.sessions[user_id]
            return "Xin lỗi, phiên làm việc bị gián đoạn. Bạn hỏi lại giúp mình nhé."

agent_manager = AgentManager()