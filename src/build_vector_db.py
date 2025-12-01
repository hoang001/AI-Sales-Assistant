import json
import os
import shutil
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings




# --- CẤU HÌNH ĐƯỜNG DẪN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'products.json')
DB_DIR = os.path.join(BASE_DIR, 'data', 'vector_db')


def load_and_process_data():
    print(f"Đang đọc dữ liệu từ: {DATA_FILE}")
    if not os.path.exists(DATA_FILE):
        print("Lỗi: Không tìm thấy file dữ liệu. Hãy chạy data_crawler.py trước!")
        return []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    documents = []
    for item in raw_data:
        # 1. Nội dung để Embed (Vector Search)
        page_content = item.get("rag_content", "")

        # 2. Metadata (Structured Search) - More detailed classification logic
        url_lower = item.get("url", "").lower()
        name_lower = item.get("name", "").lower()
        # Combine both URL and name for more accurate classification
        search_string = f"{url_lower} {name_lower}"

        # Detailed keyword lists
        laptop_keywords = [
            'laptop', 'macbook', 'surface', 'matebook', 'ideapad', 'thinkpad',
            'vivobook', 'zenbook', 'rog', 'strix', 'legion', 'predator', 'xps',
            'gram', 'spectre', 'envy', 'swift', 'aspire'
        ]
        watch_keywords = [
            'watch', 'band', 'fit', 'amazfit', 'garmin', 'galaxy-watch',
            'apple-watch', 'mi-band', 'coros', 'suunto'
        ]
        tablet_keywords = [
            'tablet', 'ipad', 'tab', 'matepad', 'galaxy-tab', 'surface-go', 'lenovo-tab'
        ]
        phone_keywords = [
            'iphone', 'samsung', 'xiaomi', 'oppo', 'phone', 'redmi', 'android',
            'galaxy', 'pixel', 'realme', 'vivo', 'nokia', 'huawei', 'oneplus',
            'vsmart', 'poco', 'z-fold', 'z-flip'
        ]

        # Classification logic with priority and default value
        cat = "Phụ kiện"  # Default to accessories

        if any(x in search_string for x in laptop_keywords):
            cat = "Laptop"
        elif any(x in search_string for x in watch_keywords):
            cat = "Đồng hồ thông minh"
        elif any(x in search_string for x in tablet_keywords):
            cat = "Tablet"
        elif any(x in search_string for x in phone_keywords):
            cat = "Điện thoại"
        # Remaining products will keep the default category "Phụ kiện"

        metadata = {
            "source": item.get("url", "unknown"),
            "name": item.get("name", "unknown"),
            "price": item.get("price_int", 0),
            "category": cat
        }

        # Create Document
        doc = Document(page_content=page_content, metadata=metadata)
        documents.append(doc)

    print(f"Đã chuẩn bị {len(documents)} documents.")
    return documents



def build_db():
    # 1. Load dữ liệu
    docs = load_and_process_data()
    if not docs: return

    # 2. Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    splits = text_splitter.split_documents(docs)
    print(f"Đã chia thành {len(splits)} chunks nhỏ.")

    # 3. Khởi tạo Embedding Model
    print("Đang tải model Embedding (có thể mất 1-2 phút lần đầu)...")
    # Thêm show_progress để bạn biết nó đang tải
    embedding_model = HuggingFaceEmbeddings(
        model_name="keepitreal/vietnamese-sbert",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    # 4. Xóa DB cũ để tránh trùng lặp
    if os.path.exists(DB_DIR):
        try:
            shutil.rmtree(DB_DIR)
            print("Đã xóa database cũ.")
        except Exception as e:
            print(f"Không thể xóa DB cũ (có thể đang mở): {e}")

    # 5. Tạo Vector DB
    print("Đang tạo Vector Database...")
    vector_db = Chroma.from_documents(
        documents=splits,
        embedding=embedding_model,
        persist_directory=DB_DIR
    )

    print(f"Thành công! Database đã được lưu tại: {DB_DIR}")

    # --- TEST NHANH ---
    print("\n---  TEST THỬ KHẢ NĂNG TÌM KIẾM ---")
    query = "Máy nào chơi game tốt giá rẻ?"
    results = vector_db.similarity_search(query, k=1)
    if results:
        print(f"Câu hỏi: {query}")
        print(f"Tìm thấy SP: {results[0].metadata.get('name')}")
        print(f"Nội dung: {results[0].page_content[:200]}...")
    else:
        print("Không tìm thấy kết quả nào.")


if __name__ == "__main__":
    build_db()