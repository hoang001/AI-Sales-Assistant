from .services import store_service

def search_products_tool(query: str):
    """Tìm kiếm sản phẩm, xem hình ảnh và giá khuyến mãi."""
    return store_service.search_products(query)

def check_stock_tool(product_name: str):
    """Kiểm tra tồn kho và giá chính xác."""
    return store_service.check_stock(product_name)

def find_store_tool(location: str):
    """
    Tìm danh sách cửa hàng CellphoneS gần nhất dựa trên địa điểm khách hàng cung cấp.
    
    Công cụ này CÓ THỂ tìm kiếm theo bất kỳ địa điểm nào: Quận, Huyện, Phường, Xã, hoặc Thành phố.
    Hãy LUÔN gọi công cụ này khi khách hàng đề cập đến địa điểm, kể cả khi chỉ có tên Phường/Xã.
    
    Input: Tên địa điểm bất kỳ (Ví dụ: "Cầu Giấy", "Quận 1", "Phường Dịch Vọng", "Vinh Hung", "Đống Đa").
    Output: Danh sách các cửa hàng gần địa điểm đó (nếu có).
    """
    return store_service.find_stores(location)

defined_tools = [search_products_tool, check_stock_tool, find_store_tool]