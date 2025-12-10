import os

# Fix lỗi import cho các phiên bản LangChain khác nhau
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

# --- CẤU HÌNH ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'data', 'vector_db')


class StoreSearchEngine:
    def __init__(self):
        print("⏳ Đang tải Search Engine...")
        # 1. Load lại Embedding Model
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="keepitreal/vietnamese-sbert",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # 2. Kết nối vào DB
        if not os.path.exists(DB_DIR):
            raise Exception(f"❌ Không tìm thấy DB tại {DB_DIR}. Hãy chạy build_vector_db.py trước!")

        self.vector_db = Chroma(
            persist_directory=DB_DIR,
            embedding_function=self.embedding_model
        )
        print("✅ Search Engine đã sẵn sàng!")

    # --- ĐÂY LÀ PHẦN BẠN ĐANG THIẾU ---
    def search(self, query, min_price=None, max_price=None, category=None, brand=None, k=5):
        """
        Tìm kiếm tối ưu với bộ lọc đa chiều: Giá + Loại + Hãng
        """
        print(f"\n🔍 Query: '{query}' | Giá: {min_price}-{max_price} | Loại: {category} | Hãng: {brand}")

        conditions = []

        # 1. Lọc theo Giá
        if min_price is not None:
            conditions.append({"price": {"$gte": min_price}})
        if max_price is not None:
            conditions.append({"price": {"$lte": max_price}})

        # 2. Lọc theo Loại (Category)
        if category:
            conditions.append({"category": category})

        # 3. Lọc theo Hãng (Brand) - PHẦN MỚI THÊM
        if brand:
            conditions.append({"brand": brand})

        # Xây dựng filter query cho ChromaDB
        if len(conditions) == 0:
            final_filter = None
        elif len(conditions) == 1:
            final_filter = conditions[0]
        else:
            final_filter = {"$and": conditions}

        # Thực hiện tìm kiếm Vector
        results = self.vector_db.similarity_search(
            query,
            k=k,
            filter=final_filter
        )
        return results


# --- PHẦN TEST (CHẠY THỬ) ---
if __name__ == "__main__":
    engine = StoreSearchEngine()

    # Test 1: Tìm kiếm thông thường
    print("\n--- Test 1: Tìm laptop chơi game ---")
    res1 = engine.search("Laptop chơi game mạnh, giá rẻ", category="Laptop", max_price=30000000)
    for doc in res1:
        print(f"- {doc.metadata['name']} ({doc.metadata['price']:,} đ)")

    # Test 2: Tìm kiếm có lọc giá và danh mục
    print("\n--- Test 2: Tìm điện thoại trên 30 triệu ---")
    res2 = engine.search("Điện thoại chụp ảnh đẹp", category="Điện thoại", min_price=30000000)
    if not res2:
        print("Không có sản phẩm nào khớp điều kiện!")
    else:
        for doc in res2:
            print(f"- {doc.metadata['name']} ({doc.metadata['price']:,} đ)")

    # Test 3: Tìm kiếm trong khoảng giá
    print("\n--- Test 3: Tìm máy trong khoảng 20-50 triệu ---")
    res3 = engine.search("Máy cấu hình mạnh", min_price=20000000, max_price=50000000)
    if not res3:
        print("Không có sản phẩm nào trong khoảng giá này!")
    else:
        for doc in res3:
            print(f"- {doc.metadata['name']} ({doc.metadata['price']:,} đ)")

    # Test 4: Tìm kiếm tablet
    print("\n--- Test 4: Tìm kiếm iPad ---")
    res4 = engine.search("iPad cho học sinh", category="Tablet", max_price=20000000)
    if not res4:
        print("Không có sản phẩm nào khớp điều kiện!")
    else:
        for doc in res4:
            print(f"- {doc.metadata['name']} ({doc.metadata['price']:,} đ)")

    # Test 5: Tìm kiếm Đồng hồ
    print("\n--- Test 4: Tìm kiếm Đồng hồ ---")
    res5 = engine.search("Đồng hồ phục vụ chạy bộ", category="Đồng hồ thông minh", max_price=2000000)
    if not res5:
        print("Không có sản phẩm nào khớp điều kiện!")
    else:
        for doc in res4:
            print(f"- {doc.metadata['name']} ({doc.metadata['price']:,} đ)")

    print("\n--- Test 3: Tìm Tablet để vẽ (Chỉ tìm trong Tablet) ---")
    # Giả sử bạn đã crawl link iPad/Galaxy Tab
    res6 = engine.search("Máy có bút cảm ứng vẽ đẹp", category="Tablet")
    for doc in res6: print(f"- {doc.metadata['name']}")

    print("\n--- Test 4: Tìm đồ Apple giá rẻ (Tìm tất cả category) ---")
    res7 = engine.search("Thiết bị Apple giá tốt", brand="Apple", max_price=15000000)
    for doc in res7: print(f"- {doc.metadata['name']} ({doc.metadata['category']})")
