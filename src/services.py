import urllib.parse
from .database import db_manager
from .config import settings

# Import Search Engine cũ
try:
    from src.search_engine import StoreSearchEngine
except ImportError:
    StoreSearchEngine = None

class StoreService:
    def __init__(self):
        print("⏳ Đang tải RAG Engine...")
        self.rag = StoreSearchEngine() if StoreSearchEngine else None

    def search_products(self, query: str, limit: int = 4):
        """Tìm kiếm & Trả về định dạng Markdown đẹp, bao gồm Đánh giá ⭐"""
        if not self.rag: return "Hệ thống tìm kiếm đang bảo trì."
        
        # 1. Tìm kiếm Vector
        results = self.rag.search(query, k=limit)
        if not results: return "Không tìm thấy sản phẩm nào."
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        response_text = ""
        
        for doc in results:
            name = doc.metadata.get('name')
            
            # 2. Lấy thông tin chi tiết từ SQL (Thêm cột rating_avg, review_count)
            cursor.execute("SELECT price_int, image_url, discount_rate, rating_avg, review_count FROM products WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            if row:
                original_price, img_url, discount, rating, reviews = row
                
                # Xử lý dữ liệu rating (tránh lỗi nếu None)
                rating = rating if rating else 0
                reviews = reviews if reviews else 0
                
                # Tạo chuỗi ngôi sao (Ví dụ: 4.5 -> ⭐⭐⭐⭐)
                star_icon = "⭐" * int(round(rating)) if rating > 0 else ""

                # Tính giá sau giảm
                final_price = original_price * (1 - discount/100)
                
                # Format hiển thị giá
                if discount > 0:
                    price_display = f"🔥 **{final_price:,.0f}đ** (Giảm {discount}% - Gốc: ~{original_price:,}đ~)"
                else:
                    price_display = f"💰 **{original_price:,.0f}đ**"
                
                # Format Markdown Card (Có thêm dòng Đánh giá)
                response_text += f"""
**{name}**
![{name}]({img_url})
- {price_display}
- {star_icon} **{rating}/5** ({reviews} đánh giá)
- 📝 *{doc.page_content[:100]}...*
---
"""
            else:
                # Fallback nếu không khớp SQL
                response_text += f"- {name} (Giá: {doc.metadata.get('price')}đ)\n"

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

    def create_order(self, customer: str, product: str, qty: int, address: str):
        """Tạo đơn hàng & Mã QR"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name, price_int, stock, discount_rate FROM products WHERE name LIKE ?", (f"%{product}%",))
            item = cursor.fetchone()
            if not item: return "Lỗi: Sản phẩm không tồn tại."
            
            real_name, price, stock, discount = item
            if stock < qty: return f"Kho chỉ còn {stock} chiếc."

            # Tính tiền
            final_unit_price = price * (1 - discount/100)
            total = int(final_unit_price * qty)
            
            # Trừ kho & Lưu đơn
            cursor.execute("UPDATE products SET stock = ? WHERE name = ?", (stock - qty, real_name))
            cursor.execute("""
                INSERT INTO orders (customer_name, product_name, quantity, total_price, address, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (customer, real_name, qty, total, address, "PENDING"))
            conn.commit()
            order_id = cursor.lastrowid
            
            # Tạo QR Code
            content = f"DH{order_id} {customer}"
            qr_url = f"https://img.vietqr.io/image/{settings.BANK_ID}-{settings.BANK_ACC}-compact.png?amount={total}&addInfo={urllib.parse.quote(content)}"
            
            return (f"🎉 **ĐẶT HÀNG THÀNH CÔNG #{order_id}**\n"
                    f"- Khách hàng: {customer}\n"
                    f"- Địa chỉ: {address}\n"
                    f"- Tổng tiền: **{total:,}đ**\n\n"
                    f"👇 **Quét mã để thanh toán:**\n"
                    f"![QR Thanh Toán]({qr_url})")
            
        except Exception as e:
            return f"Lỗi hệ thống: {e}"
        finally:
            conn.close()

store_service = StoreService()