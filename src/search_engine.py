import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma

# --- CẤU HÌNH ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'data', 'vector_db')


class StoreSearchEngine:
    def __init__(self):
        print("⏳ Đang tải Search Engine...")
        # 1. Load lại Embedding Model (phải giống hệt lúc Build DB)
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="keepitreal/vietnamese-sbert",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # 2. Kết nối vào DB đã lưu trên ổ cứng
        if not os.path.exists(DB_DIR):
            raise Exception(f"❌ Không tìm thấy DB tại {DB_DIR}. Hãy chạy build_vector_db.py trước!")

        self.vector_db = Chroma(
            persist_directory=DB_DIR,
            embedding_function=self.embedding_model
        )
        print("✅ Search Engine đã sẵn sàng!")

    def search(self, query, category=None, min_price=None, max_price=None, k=3):
        """
        Tìm kiếm sản phẩm theo ngữ nghĩa + Lọc theo giá và danh mục
        :param query: Câu hỏi của người dùng (VD: "Máy nào pin trâu")
        :param category: Danh mục sản phẩm (VD: "Điện thoại")
        :param min_price: Giá thấp nhất (VNĐ)
        :param max_price: Giá cao nhất (VNĐ)
        :param k: Số lượng kết quả muôn lấy
        """
        print(f"\n🔍 Query: '{query}' | Category: {category} | Giá: {min_price}-{max_price}")

        # --- THỰC HIỆN TÌM KIẾM ---
        try:
            # Lấy nhiều kết quả hơn để có đủ lựa chọn sau khi lọc
            results = self.vector_db.similarity_search(query, k=k * 5)
        except Exception as e:
            print(f"⚠️ Lỗi tìm kiếm: {e}")
            return []

        # --- LỌC KẾT QUẢ SAU KHI TÌM KIẾM ---
        filtered_results = []
        seen_identifiers = set()  # Chống trùng lặp bằng URL hoặc Tên sản phẩm

        for doc in results:
            metadata = doc.metadata

            # Sử dụng URL làm định danh chính, nếu không có thì dùng Tên sản phẩm
            identifier = metadata.get('url') or metadata.get('name')

            # Bỏ qua nếu đã thấy định danh này
            if identifier and identifier in seen_identifiers:
                continue

            # 1. Lọc theo danh mục
            if category:
                doc_category = metadata.get('category', '').lower()
                if category.lower() not in doc_category:
                    continue

            # 2. Lọc theo giá
            price = metadata.get('price', 0)
            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue

            # Nếu qua hết các bộ lọc, thêm vào kết quả
            filtered_results.append(doc)
            if identifier:
                seen_identifiers.add(identifier)

            # Dừng khi đã đủ số lượng
            if len(filtered_results) >= k:
                break

        return filtered_results


# --- PHẦN TEST (CHẠY THỬ) ---
if __name__ == "__main__":
    engine = StoreSearchEngine()

    # Test 1: Tìm kiếm thông thường
    print("\n--- Test 1: Tìm laptop chơi game ---")
    res1 = engine.search("Laptop chơi game mạnh", category="Laptop")
    for doc in res1:
        print(f"- {doc.metadata['name']} ({doc.metadata['price']:,} đ)")

    # Test 2: Tìm kiếm có lọc giá và danh mục
    print("\n--- Test 2: Tìm điện thoại trên 60 triệu ---")
    res2 = engine.search("Điện thoại chụp ảnh đẹp", category="Điện thoại",min_price=60000000)
    if not res2:
        print("👉 Không có sản phẩm nào khớp điều kiện!")
    else:
        for doc in res2:
            print(f"- {doc.metadata['name']} ({doc.metadata['price']:,} đ)")

    # Test 3: Tìm kiếm trong khoảng giá
    print("\n--- Test 3: Tìm máy trong khoảng 15-25 triệu ---")
    res3 = engine.search("Laptop", category="Laptop", min_price=15000000, max_price=25000000)
    if not res3:
        print("👉 Không có sản phẩm nào trong khoảng giá này!")
    else:
        for doc in res3:
            print(f"- {doc.metadata['name']} ({doc.metadata['price']:,} đ)")
