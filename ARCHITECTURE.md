# 📋 KIẾN TRÚC DỰ ÁN AI-SALES-ASSISTANT

## 🔗 SƠ ĐỒ KẾT NỐI CÁC FILE

```
run.py (Entry Point - FastAPI Server)
    ↓
src/main.py (FastAPI App + CORS)
    ├─→ POST /chat endpoint
    │   └─→ agent_manager.get_response()
    │
    ├─→ db_manager.initialize_db()
    └─→ Khởi động Server ở port 8000
        
        
src/agent.py (AgentManager - Trung tâm điều phối)
    ↓
    ├─→ genai.configure(API key từ config)
    ├─→ genai.GenerativeModel('gemini-2.5-flash-lite')
    ├─→ Tích hợp system_instruction từ prompts.py
    ├─→ Tích hợp tools từ tools.py
    ├─→ start_chat() với enable_automatic_function_calling=True
    └─→ Trả về response.text cho client
    

src/tools.py (Định nghĩa 3 Tool cho AI)
    ├─→ search_products_tool()
    │   └─→ store_service.search_products()
    │
    ├─→ check_stock_tool()
    │   └─→ store_service.check_stock()
    │
    └─→ place_order_tool()
        └─→ store_service.create_order()


src/services.py (StoreService - Business Logic)
    ├─→ search_products()
    │   ├─→ self.rag.search() (từ search_engine.py)
    │   ├─→ db_manager.get_connection()
    │   ├─→ Query SQL: SELECT từ products table
    │   └─→ Return Markdown format với giá, đánh giá, hình ảnh
    │
    ├─→ check_stock()
    │   ├─→ db_manager.get_connection()
    │   ├─→ Query SQL: SELECT name, price, stock, discount
    │   └─→ Return thông tin kho hàng
    │
    └─→ create_order()
        ├─→ db_manager.get_connection()
        ├─→ INSERT vào orders table
        └─→ Return QR code thanh toán


src/search_engine.py (StoreSearchEngine - RAG/Vector Search)
    ├─→ HuggingFaceEmbeddings (Vietnamese SBERT)
    ├─→ Chroma Vector DB (từ data/vector_db/)
    ├─→ search() method
    └─→ extract_price_intent() - phân tích giá từ câu nói


src/database.py (DatabaseManager - SQLite)
    ├─→ get_connection()
    ├─→ initialize_db()
    │   ├─→ CREATE TABLE products (id, name, price_int, stock, category, discount_rate, rating_avg, review_count, rag_content)
    │   └─→ CREATE TABLE orders (order_id, customer_name, product_name, quantity, total_price, address, status, created_at)
    └─→ Query methods


src/config.py (Cấu hình toàn bộ dự án)
    ├─→ Load .env file
    ├─→ GEMINI_API_KEY
    ├─→ DB_PATH = store.db
    ├─→ RAW_DATA_PATH = data/raw/products.json
    ├─→ VECTOR_DB_PATH = data/vector_db/
    ├─→ BANK_ID, BANK_ACC (cho QR thanh toán)
    └─→ Được import bởi: agent.py, database.py, search_engine.py, services.py


src/prompts.py (System Instruction cho AI)
    └─→ sales_system_instruction
        ├─→ Prompt chi tiết về quy trình bán hàng
        ├─→ Luật "SHOOT FIRST" (gợi ý ngay)
        ├─→ Quy trình kiểm tra địa chỉ trước khi đặt hàng
        └─→ Được gọi trong agent.py


src/build_vector_db.py (Xây dựng Vector DB - Chạy một lần)
    ├─→ Load data/raw/products.json
    ├─→ Tạo Document + Metadata
    ├─→ Split text (RecursiveCharacterTextSplitter)
    ├─→ Embed với HuggingFaceEmbeddings
    └─→ Lưu vào Chroma DB tại data/vector_db/


## ✅ TRẠNG THÁI KẾT NỐI

### Các File Đã Kết Nối Hoàn Chỉnh:
- ✅ run.py → src/main.py (FastAPI startup)
- ✅ main.py → agent.py (AgentManager init)
- ✅ agent.py → config.py (Load GEMINI_API_KEY)
- ✅ agent.py → prompts.py (system_instruction)
- ✅ agent.py → tools.py (defined_tools)
- ✅ tools.py → services.py (store_service methods)
- ✅ services.py → search_engine.py (RAG search)
- ✅ services.py → database.py (SQL queries)
- ✅ database.py → config.py (DB_PATH)
- ✅ search_engine.py → config.py (VECTOR_DB_PATH)
- ✅ main.py → database.py (initialize_db on startup)

### Luồng Dữ Liệu Khi Khách Chat:

1. **Client gửi:** `POST /chat` với `{message: "...", user_id: "..."}`
2. **main.py** nhận request
3. **agent_manager.get_response()** được gọi
4. **Gemini AI** xử lý message với tools
5. **AI tự động gọi tool** (search/check/order)
6. **Tool gọi service method**
7. **Service query database + search engine**
8. **Kết quả trả về AI**
9. **AI format response** và gửi lại client

### Điểm Yếu Cần Chú Ý:

⚠️ **1. build_vector_db.py chưa chạy?**
   - Vector DB cần được tạo trước lần chạy đầu tiên
   - Chạy: `python -m src.build_vector_db`
   - Nếu chưa chạy, search_engine.py sẽ báo "Chưa có dữ liệu Vector"

⚠️ **2. data/raw/products.json chưa có?**
   - data_crawler.py cần chạy để crawl dữ liệu
   - Hoặc import dữ liệu từ nguồn khác
   - Chạy: `python -m src.data_crawler`

⚠️ **3. .env chưa cấu hình?**
   - GEMINI_API_KEY phải có giá trị hợp lệ
   - Nếu không, agent.py sẽ fail

⚠️ **4. store.db chưa tồn tại?**
   - main.py sẽ tự tạo khi khởi động (db_manager.initialize_db())
   - Nhưng phải import dữ liệu sản phẩm vào table


## 🚀 BƯỚC CHẠY HOÀN CHỈNH:

### 1️⃣ Chuẩn bị dữ liệu:
```bash
# Nếu chưa có data/raw/products.json
python -m src.data_crawler

# Hoặc tạo file products.json thủ công
```

### 2️⃣ Xây dựng Vector DB:
```bash
python -m src.build_vector_db
```

### 3️⃣ Cấu hình .env:
```
GEMINI_API_KEY=your_valid_api_key_here
```

### 4️⃣ Chạy Server:
```bash
python run.py
```

### 5️⃣ Test API:
- Truy cập: http://localhost:8000/docs
- POST /chat với body: `{"message": "Tôi muốn mua laptop", "user_id": "user123"}`


## 📊 TÓMLẠI KẾT NỐI:

- **Hoàn toàn kết nối ✅** giữa API, Agent, Tools, Services, Database, Search Engine
- **Còn thiếu ⚠️:** Dữ liệu sản phẩm (products.json), Vector DB đã xây dựng
- **Có thể chạy ngay?** ✅ CÓ - nếu .env có API key hợp lệ
- **Hiển thị giá + đánh giá?** ✅ CÓ - services.py đã format đầy đủ

---
*Tạo lúc: 2025-12-11*
