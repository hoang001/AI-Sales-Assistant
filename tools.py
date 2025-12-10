# tools.py

# 1. Dữ liệu giả (Mock Data)
MOCK_DATABASE = [
    {"id": "L01", "name": "Laptop Gaming Asus TUF", "price": 20000000, "category": "Laptop", "stock": 5},
    {"id": "L02", "name": "MacBook Air M1", "price": 18000000, "category": "Laptop", "stock": 0},
    {"id": "P01", "name": "iPhone 15 Pro Max", "price": 30000000, "category": "Phone", "stock": 10},
    {"id": "A01", "name": "Tai nghe Sony WH-1000XM5", "price": 8000000, "category": "Accessory", "stock": 2}
]

# 2. Định nghĩa hàm tìm kiếm (Đây là Tool mà AI sẽ gọi)
def search_products(keyword: str):
    """
    Tìm kiếm sản phẩm trong kho theo tên hoặc từ khóa.
    Args:
        keyword (str): Từ khóa sản phẩm khách muốn tìm (vd: 'iphone', 'asus', 'laptop').
    """
    print(f"\n[SYSTEM LOG] AI đang gọi tool tìm kiếm: '{keyword}'...") # Log để bạn biết AI đang hoạt động
    
    results = []
    for item in MOCK_DATABASE:
        if keyword.lower() in item['name'].lower():
            results.append(item)
    
    if not results:
        return "Không tìm thấy sản phẩm nào khớp với từ khóa."
    
    return results

def check_stock_status(product_name: str):
    """
    Kiểm tra tình trạng còn hàng hay hết hàng của một sản phẩm cụ thể.
    Args:
        product_name (str): Tên sản phẩm cần kiểm tra.
    """
    print(f"\n[SYSTEM LOG] AI đang kiểm tra kho: '{product_name}'...")
    
    for item in MOCK_DATABASE:
        if product_name.lower() in item['name'].lower():
            if item['stock'] > 0:
                return f"Sản phẩm {item['name']} còn {item['stock']} cái."
            else:
                return f"Sản phẩm {item['name']} hiện đã HẾT HÀNG."
    return "Không tìm thấy thông tin sản phẩm."

# Danh sách tool để nạp vào model
sales_tools = [search_products, check_stock_status]