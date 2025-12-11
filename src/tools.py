from .services import store_service

def search_products_tool(query: str):
    """Tìm kiếm sản phẩm, xem hình ảnh và giá khuyến mãi."""
    return store_service.search_products(query)

def check_stock_tool(product_name: str):
    """Kiểm tra tồn kho và giá chính xác."""
    return store_service.check_stock(product_name)

def place_order_tool(customer_name: str, product_name: str, quantity: int, address: str):
    """Đặt hàng và lấy mã QR thanh toán."""
    return store_service.create_order(customer_name, product_name, quantity, address)

defined_tools = [search_products_tool, check_stock_tool, place_order_tool]