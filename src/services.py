import urllib.parse
import json
import os
from .database import db_manager
from .config import settings
import unicodedata

# Import Search Engine
try:
    from src.search_engine import StoreSearchEngine
except ImportError:
    StoreSearchEngine = None

class StoreService:
    def __init__(self):
        print("⏳ Đang tải RAG Engine...")
        self.rag = StoreSearchEngine() if StoreSearchEngine else None

    def search_products(self, query: str, limit: int = 10):
        """
        Tìm kiếm sản phẩm bằng RAG Vector + SQL.
        Trả về định dạng Markdown bao gồm: Ảnh, Giá, Đánh giá, Thông số.
        """
        if not self.rag: return "Hệ thống tìm kiếm đang bảo trì."
        
        # 1. Tìm kiếm Vector (Tìm theo ý hiểu)
        results = self.rag.search(query, k=limit)
        if not results: return "Không tìm thấy sản phẩm nào phù hợp."
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        response_text = ""
        print(f"\n--- DEBUG TÌM ẢNH ({len(results)} kết quả) ---")
        
        for doc in results:
            name = doc.metadata.get('name')
            
            # [QUAN TRỌNG] Lấy thêm cột 'rag_content' để hiển thị thông số kỹ thuật cho Frontend V4
            # Dùng LIKE để tìm kiếm linh hoạt hơn (tránh lỗi lệch tên)
            cursor.execute("SELECT price_int, image_url, discount_rate, rating_avg, review_count, rag_content FROM products WHERE name LIKE ? LIMIT 1", (f"%{name}%",))
            row = cursor.fetchone()
            
            if row:
                original_price, img_url, discount, rating, reviews, specs_text = row
                
                print(f"✅ Tìm thấy SQL: {name} | Ảnh: {str(img_url)[:30]}...")

                # 1. Xử lý URL ảnh an toàn
                if img_url and len(str(img_url)) > 5:
                    img_url = urllib.parse.quote(img_url, safe=":/?#[]@!$&'()*+,;=")
                else:
                    img_url = "https://via.placeholder.com/300x300?text=No+Image"

                # 2. Xử lý dữ liệu hiển thị (Rating, Stars)
                rating = rating if rating else 0
                reviews = reviews if reviews else 0
                star_icon = "⭐" * int(round(rating)) if rating > 0 else ""

                # 3. Xử lý thông số kỹ thuật (Cắt ngắn cho gọn để hiển thị đẹp trên Card)
                if specs_text:
                    # Loại bỏ phần tên lặp lại ở đầu chuỗi rag_content
                    # Ví dụ: "Sản phẩm: iPhone 15. Cấu hình:..." -> "Cấu hình:..."
                    short_specs = specs_text.replace(f"Sản phẩm: {name}.", "").strip()
                    # Lấy khoảng 150 ký tự đầu tiên
                    short_specs = short_specs[:160] + "..." if len(short_specs) > 160 else short_specs
                else:
                    short_specs = "Đang cập nhật..."

                # 4. Tính giá khuyến mãi
                final_price = original_price * (1 - discount/100)
                
                if discount > 0:
                    price_display = f"🔥 **{final_price:,.0f}đ** (Giảm {discount}% - Gốc: ~{original_price:,.0f}đ~)"
                else:
                    price_display = f"💰 **{original_price:,.0f}đ**"
                
                # 5. Tạo Markdown chuẩn (Frontend bắt buộc phải theo format này để render thẻ)
                # Format: **Tên** \n ![Ảnh](URL) \n - Giá \n - Rating \n - Thông số \n - Mô tả
                response_text += f"""
**{name}**
![{name}]({img_url})
- {price_display}
- {star_icon} **{rating}/5** ({reviews} đánh giá)
- ⚙️ Thông số: {short_specs}
- 📝 *{doc.page_content[:100]}...*
---
"""
            else:
                print(f"❌ Không tìm thấy trong SQL: {name} (Sẽ mất ảnh)")
                # Fallback: Trả về thông tin cơ bản từ Vector DB nếu không khớp SQL
                price_vec = doc.metadata.get('price', 0)
                response_text += f"- **{name}** (Giá tham khảo: {price_vec:,.0f}đ)\n"

        conn.close()
        return response_text

    def check_stock(self, product_name: str):
        """Kiểm tra tồn kho"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, price_int, stock, discount_rate FROM products WHERE name LIKE ?", (f"%{product_name}%",))
        item = cursor.fetchone()
        conn.close()
        
        if item:
            name, price, stock, discount = item
            final_price = price * (1 - discount/100)
            status = f"✅ CÒN {stock} chiếc" if stock > 0 else "❌ HẾT HÀNG"
            return f"Sản phẩm **{name}**\n- Tình trạng: {status}\n- Giá hiện tại: {final_price:,.0f}đ (Đã giảm {discount}%)"
        return "Không tìm thấy sản phẩm này."

    def remove_accents(self, input_str):
        if not input_str: return ""
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    def find_stores(self, location: str):
        """Tìm cửa hàng CellphoneS (Phiên bản chấp nhận không dấu và tìm kiếm linh hoạt)"""
        import json
        import os
        import time
        
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            store_path = os.path.join(base_dir, 'data', 'raw', 'store.json')
            with open(store_path, 'r', encoding='utf-8') as f:
                all_stores = json.load(f)
        except Exception as e:
            print(f"❌ Lỗi đọc file store.json: {e}")
            return "⚠️ Hệ thống đang bảo trì dữ liệu cửa hàng."

        # 1. Chuẩn hóa từ khóa tìm kiếm (Xóa dấu, chữ thường, loại bỏ các từ chỉ địa danh hành chính)
        # Ví dụ: "Phường Vinh Hưng" -> "vinh hung", "Quận Cầu Giấy" -> "cau giay"
        loc_norm = self.remove_accents(location.lower())
        # Loại bỏ các từ chỉ địa danh hành chính
        loc_norm = loc_norm.replace("quan", "").replace("huyen", "").replace("thanh pho", "").replace("tp", "").replace("phuong", "").replace("xa", "").replace("ward", "").replace("district", "").strip()
        # Xóa các ký tự đặc biệt và khoảng trắng thừa
        loc_norm = " ".join(loc_norm.split())
        
        #region agent log
        with open(r"d:\HOCTAP\KHMT\AI-Sales-Assistant\.cursor\debug.log", "a", encoding="utf-8") as _f:
            _f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "post-fix",
                "hypothesisId": "H1",
                "location": "services.py:141",
                "message": "find_stores entry",
                "data": {"raw_location": location, "loc_norm": loc_norm},
                "timestamp": int(time.time() * 1000)
            }) + "\n")
        #endregion
        
        if not loc_norm:
            return f"Dạ em không hiểu địa điểm '{location}'. Anh/chị vui lòng nhập tên Quận/Huyện hoặc Phường/Xã cụ thể hơn ạ."
        
        found_stores = []
        words = [w for w in loc_norm.split() if len(w) > 1]
        #region agent log
        with open(r"d:\HOCTAP\KHMT\AI-Sales-Assistant\.cursor\debug.log", "a", encoding="utf-8") as _f:
            _f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "post-fix",
                "hypothesisId": "H4",
                "location": "services.py:159",
                "message": "tokenized_location",
                "data": {"loc_norm": loc_norm, "words": words, "word_count": len(words)},
                "timestamp": int(time.time() * 1000)
            }) + "\n")
        #endregion

        # 2. So sánh thông minh (tìm kiếm trong cả address và city)
        for store in all_stores:
            # Chuẩn hóa địa chỉ trong DB (xóa dấu, chữ thường)
            addr_norm = self.remove_accents(store.get('address', '').lower())
            city_norm = self.remove_accents(store.get('city', '').lower())
            name_norm = self.remove_accents(store.get('name', '').lower())

            matched = False
            match_reason = ""

            # Ưu tiên khớp cụm đầy đủ
            if (loc_norm and (loc_norm in addr_norm or loc_norm in city_norm or loc_norm in name_norm)):
                matched = True
                match_reason = "full_loc_norm"
            # Nếu có >=2 từ: yêu cầu TẤT CẢ từ phải xuất hiện trong CÙNG MỘT trường (address HOẶC city HOẶC name)
            # QUAN TRỌNG: Dùng TẤT CẢ từ (không filter), để tránh mất từ ngắn như "my" trong "my dinh"
            elif len(words) >= 2:
                # Kiểm tra xem tất cả từ có xuất hiện trong cùng một trường không
                if (all(word in addr_norm for word in words) or
                    all(word in city_norm for word in words) or
                    all(word in name_norm for word in words)):
                    matched = True
                    match_reason = "all_words_match_same_field"
            # Nếu chỉ 1 từ: yêu cầu từ đủ dài (>3) và xuất hiện trong địa chỉ/tên/thành phố
            elif len(words) == 1:
                w = words[0]
                if len(w) > 3 and (w in addr_norm or w in city_norm or w in name_norm):
                    matched = True
                    match_reason = "single_word"

            if matched:
                found_stores.append(store)
                #region agent log
                if len(found_stores) <= 5:
                    with open(r"d:\HOCTAP\KHMT\AI-Sales-Assistant\.cursor\debug.log", "a", encoding="utf-8") as _f:
                        _f.write(json.dumps({
                            "sessionId": "debug-session",
                            "runId": "post-fix",
                            "hypothesisId": "H2",
                            "location": "services.py:204",
                            "message": "match_found",
                            "data": {
                                "loc_norm": loc_norm,
                                "words": words,
                                "word_count": len(words),
                                "matched_store": store.get('name'),
                                "store_address": store.get('address', '')[:60],
                                "store_city": store.get('city', ''),
                                "reason": match_reason,
                                "addr_contains_all_words": all(word in addr_norm for word in words) if len(words) >= 2 else None,
                                "city_contains_all_words": all(word in city_norm for word in words) if len(words) >= 2 else None
                            },
                            "timestamp": int(time.time() * 1000)
                        }) + "\n")
                #endregion
        
        if not found_stores:
            #region agent log
            with open(r"d:\HOCTAP\KHMT\AI-Sales-Assistant\.cursor\debug.log", "a", encoding="utf-8") as _f:
                _f.write(json.dumps({
                    "sessionId": "debug-session",
                    "runId": "post-fix",
                    "hypothesisId": "H3",
                    "location": "services.py:237",
                    "message": "no_store_found",
                    "data": {"loc_norm": loc_norm, "words": words, "word_count": len(words)},
                    "timestamp": int(time.time() * 1000)
                }) + "\n")
            #endregion
            return f"Dạ em chưa tìm thấy chi nhánh ở khu vực '{location}'. Anh/chị thử nhập tên Quận/Huyện lớn hơn xem sao ạ? (Ví dụ: 'Cầu Giấy', 'Đống Đa', 'Quận 1')"

        display_stores = found_stores[:5]
        response_text = f"🎉 Tìm thấy **{len(found_stores)}** cửa hàng gần **{location}**:\n\n"
        
        for s in display_stores:
            response_text += f"🏠 **{s['name']}**\n- 📍 {s['address']}\n- 🗺️ [Xem bản đồ]({s['map_url']})\n---\n"
            
        return response_text

store_service = StoreService()