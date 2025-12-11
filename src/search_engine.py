from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
import re # <--- Cần thêm thư viện này để bắt số tiền
from .config import settings

class StoreSearchEngine:
    def __init__(self):
        # Cấu hình Embedding
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="keepitreal/vietnamese-sbert"
        )
        
        # Kết nối ChromaDB
        if os.path.exists(settings.VECTOR_DB_PATH) and os.listdir(settings.VECTOR_DB_PATH):
            self.vector_db = Chroma(
                persist_directory=str(settings.VECTOR_DB_PATH),
                embedding_function=self.embedding_model
            )
            print(f"✅ RAG: Đã kết nối DB tại {settings.VECTOR_DB_PATH}")
        else:
            self.vector_db = None
            print("⚠️ RAG: Chưa có dữ liệu Vector. Hãy chạy 'python -m src.build_vector_db'")

    # --- HÀM MỚI: BÓC TÁCH GIÁ TIỀN TỪ CÂU NÓI ---
    def extract_price_intent(self, query: str):
        """
        Phân tích câu nói để tìm ý định về giá.
        Ví dụ: "tầm 20 triệu" -> min=18tr, max=22tr
        """
        text = query.lower().replace(".", "").replace(",", "") # Xóa dấu chấm phẩy cho dễ xử lý
        
        # 1. Tìm con số đi kèm với từ chỉ tiền (tr, triệu, k, nghìn...)
        # Pattern: (số) + (khoảng trắng tùy ý) + (đơn vị)
        match = re.search(r"(\d+)\s*(tr|triệu|m|k|nghìn|củ)", text)
        
        if not match:
            return None, None
            
        number = int(match.group(1))
        unit = match.group(2)
        
        # Chuẩn hóa về VNĐ
        price_value = 0
        if unit in ['tr', 'triệu', 'm', 'củ']:
            price_value = number * 1_000_000
        elif unit in ['k', 'nghìn']:
            price_value = number * 1_000
            
        # 2. Xử lý logic "Khoảng", "Dưới", "Trên"
        min_price = None
        max_price = None
        
        if "dưới" in text or "tối đa" in text or "nhỏ hơn" in text:
            max_price = price_value
        elif "trên" in text or "hơn" in text or "tối thiểu" in text:
            min_price = price_value
        else:
            # Mặc định hiểu là "KHOẢNG" (Dao động 10%)
            min_price = int(price_value * 0.9)
            max_price = int(price_value * 1.1)
            
        return min_price, max_price

    def search(self, query: str, k=5):
        if not self.vector_db:
            return []

        # 1. Tự động trích xuất giá từ câu query
        detected_min, detected_max = self.extract_price_intent(query)
        
        print(f"🔍 Query: '{query}' | Giá detect: {detected_min:,} - {detected_max:,}" if detected_min else f"🔍 Query: '{query}' | Giá: Không rõ")

        # 2. Tạo bộ lọc Metadata cho ChromaDB
        # Lưu ý: ChromaDB filter cú pháp: {"metadata_field": {"$operator": value}}
        filter_dict = {}
        conditions = []

        if detected_min is not None:
            conditions.append({"price": {"$gte": detected_min}})
        if detected_max is not None:
            conditions.append({"price": {"$lte": detected_max}})

        # Logic ghép bộ lọc (ChromaDB yêu cầu $and nếu có nhiều điều kiện)
        if len(conditions) > 1:
            filter_dict = {"$and": conditions}
        elif len(conditions) == 1:
            filter_dict = conditions[0]
        else:
            filter_dict = None # Không lọc gì cả

        # 3. Thực hiện tìm kiếm
        try:
            results = self.vector_db.similarity_search(
                query,
                k=k,
                filter=filter_dict # Truyền bộ lọc vào đây
            )
            return results
        except Exception as e:
            print(f"❌ Lỗi tìm kiếm ChromaDB: {e}")
            return self.vector_db.similarity_search(query, k=k)