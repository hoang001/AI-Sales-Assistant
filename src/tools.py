from .services import store_service

def tool_search(query: str):
    """Tìm kiếm sản phẩm theo mô tả."""
    return store_service.search_products(query)

def tool_check_stock(product_name: str):
    """Kiểm tra tồn kho."""
    return store_service.check_stock(product_name)

def tool_place_order(customer_name: str, product_name: str, quantity: int, address: str):
    """Đặt hàng và nhận mã QR."""
    return store_service.create_order(customer_name, product_name, quantity, address)

defined_tools = [tool_search, tool_check_stock, tool_place_order]