# src/services.py
import urllib.parse
from .database import db_manager
from .config import settings
# Import RAG Engine cũ của bạn
try:
    from src.search_engine import StoreSearchEngine
except ImportError:
    StoreSearchEngine = None

class StoreService:
    def __init__(self):
        self.rag = StoreSearchEngine() if StoreSearchEngine else None

    def search_products(self, query: str, limit: int = 5): # Tăng limit lên 5 để AI có nhiều lựa chọn so sánh
        """Logic tìm kiếm RAG kết hợp lấy giá khuyến mãi từ SQL"""
        if not self.rag:
            return "Hệ thống tìm kiếm đang bảo trì."
        
        # 1. Tìm kiếm ngữ nghĩa bằng Vector
        results = self.rag.search(query, k=limit)
        if not results:
            return "Không tìm thấy sản phẩm nào."
            
        # 2. Lấy thêm thông tin khuyến mãi từ SQL để làm giàu dữ liệu
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        info = ""
        for doc in results:
            name = doc.metadata.get('name')
            # Lấy giá gốc từ Vector DB (hoặc có thể query lại SQL cho chuẩn)
            original_price = doc.metadata.get('price', 0)
            
            # Query SQL xem có giảm giá không
            cursor.execute("SELECT discount_rate FROM products WHERE name = ?", (name,))
            row = cursor.fetchone()
            discount = row[0] if row else 0
            
            # Tính toán giá sau giảm
            final_price = original_price * (1 - discount/100)
            
            # Format văn bản để "mớm" lời cho AI
            if discount > 0:
                price_str = f"GIÁ SỐC: {final_price:,.0f}đ (Gốc: {original_price:,}đ - Giảm {discount}%)"
            else:
                price_str = f"Giá: {original_price:,}đ"
                
            desc = doc.page_content[:200]
            info += f"- {name} | {price_str} | Đặc điểm: {desc}...\n"
            
        conn.close()
        return info

    def check_stock(self, product_name: str):
        """Logic kiểm tra kho SQL"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, price_int, stock FROM products WHERE name LIKE ?", (f"%{product_name}%",))
        item = cursor.fetchone()
        conn.close()
        
        if item:
            name, price, stock = item
            state = f"CÒN {stock}" if stock > 0 else "HẾT HÀNG"
            return f"Sản phẩm '{name}' hiện {state}. Giá: {price:,}đ."
        return "Không tìm thấy sản phẩm này trong kho."

    def create_order(self, customer: str, product: str, qty: int, address: str):
        """Logic tạo đơn hàng & QR"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Tìm & Check kho
            cursor.execute("SELECT name, price_int, stock FROM products WHERE name LIKE ?", (f"%{product}%",))
            item = cursor.fetchone()
            if not item: return "Lỗi: Sản phẩm không tồn tại."
            
            real_name, price, stock = item
            if stock < qty: return f"Lỗi: Kho chỉ còn {stock} chiếc."

            # 2. Trừ kho & Tạo đơn
            total = price * qty
            cursor.execute("UPDATE products SET stock = ? WHERE name = ?", (stock - qty, real_name))
            cursor.execute("""
                INSERT INTO orders (customer_name, product_name, quantity, total_price, address, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (customer, real_name, qty, total, address, "NEW"))
            conn.commit()
            order_id = cursor.lastrowid
            
            # 3. Tạo QR
            content = f"DH{order_id} {customer}"
            qr_url = f"https://img.vietqr.io/image/{settings.BANK_ID}-{settings.BANK_ACC}-compact.png?amount={total}&addInfo={urllib.parse.quote(content)}"
            
            return (f"✅ ĐÃ ĐẶT HÀNG #{order_id}\n"
                    f"Khách: {customer} - {address}\n"
                    f"Tổng: {total:,}đ\n"
                    f"Quét mã để thanh toán:\n![QR]({qr_url})")
            
        except Exception as e:
            return f"Lỗi hệ thống: {e}"
        finally:
            conn.close()

store_service = StoreService()