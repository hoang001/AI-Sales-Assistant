import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma

# --- CẤU HÌNH ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'data', 'vector_db')


class StoreSearchEngine:
    def __init__(self):
        print("Đang tải Search Engine...")
        # 1. Load lại Embedding Model (phải giống hệt lúc Build DB)
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="keepitreal/vietnamese-sbert",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # 2. Kết nối vào DB đã lưu trên ổ cứng
        if not os.path.exists(DB_DIR):
            raise Exception(f"Không tìm thấy DB tại {DB_DIR}. Hãy chạy build_vector_db.py trước!")

        self.vector_db = Chroma(
            persist_directory=DB_DIR,
            embedding_function=self.embedding_model
        )
        print("Search Engine đã sẵn sàng!")

    def search(self, query, category=None, min_price=None, max_price=None, k=5):
        """
        Tìm kiếm sản phẩm hiệu quả hơn bằng cách sử dụng metadata filtering của ChromaDB.
        :param query: Câu hỏi của người dùng (VD: "Máy nào pin trâu")
        :param category: Danh mục sản phẩm (VD: "Điện thoại", "Laptop", "Tablet")
        :param min_price: Giá thấp nhất (VNĐ)
        :param max_price: Giá cao nhất (VNĐ)
        :param k: Số lượng kết quả muốn lấy
        """
        print(f"\nQuery: '{query}' | Category: {category} | Giá: {min_price}-{max_price}")

        # --- XÂY DỰNG BỘ LỌC METADATA (PRE-FILTERING) ---
        # Tối ưu: Lọc ở tầng database trước khi tìm kiếm vector sẽ nhanh hơn nhiều.
        where_filter = {}
        conditions = []
        if category:
            # Quan trọng: ChromaDB phân biệt hoa thường.
            # Category đã được lưu với chữ cái đầu viết hoa ("Laptop", "Tablet",...)
            conditions.append({'category': {'$eq': category}})
        if min_price is not None:
            conditions.append({'price': {'$gte': min_price}})
        if max_price is not None:
            conditions.append({'price': {'$lte': max_price}})

        if conditions:
            if len(conditions) > 1:
                where_filter = {'$and': conditions}
            else:
                where_filter = conditions[0]

        # --- THỰC HIỆN TÌM KIẾM ---
        try:
            # Sử dụng `filter` để áp dụng bộ lọc metadata ở tầng DB
            results = self.vector_db.similarity_search(
                query,
                k=k * 2,  # Lấy nhiều hơn k một chút để khử trùng lặp
                filter=where_filter if where_filter else None
            )
        except Exception as e:
            print(f"Lỗi tìm kiếm: {e}")
            return []

        # --- KHỬ TRÙNG LẶP KẾT QUẢ ---
        # Mặc dù đã lọc, có thể nhiều chunks của cùng 1 sản phẩm được trả về.
        # Chúng ta chỉ muốn hiển thị mỗi sản phẩm (source URL.txt) một lần.
        final_results = []
        seen_sources = set()
        for doc in results:
            source = doc.metadata.get('source')
            if source and source not in seen_sources:
                final_results.append(doc)
                seen_sources.add(source)
            if len(final_results) >= k:
                break

        return final_results


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
