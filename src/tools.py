from .services import store_service


def search_products_tool(query: str):
    """Tìm kiếm sản phẩm, xem hình ảnh và giá khuyến mãi."""
    return store_service.search_products(query)


def check_stock_tool(product_name: str):
    """Kiểm tra tồn kho và giá chính xác."""
    return store_service.check_stock(product_name)


def find_store_tool(location: str):
    """
    Tìm cửa hàng CellphoneS gần nhất.

    - Nếu input dạng GPS:lat,lng → dùng Google Places → HTML card
    - Nếu input là chữ (Quận/Huyện/Phường) → dùng SerpAPI → text
    """

    # ==========================
    # TRƯỜNG HỢP GPS
    # ==========================
    if isinstance(location, str) and location.startswith("GPS:"):
        try:
            _, coords = location.split("GPS:")
            lat_str, lng_str = coords.split(",")
            lat = float(lat_str.strip())
            lng = float(lng_str.strip())

            # GỌI ĐÚNG HÀM HTML CARD
            return store_service.find_nearest_store(lat, lng)

        except Exception as e:
            return f"<div class='error-message'>❌ Lỗi GPS: {e}</div>"

    # ==========================
    # TRƯỜNG HỢP TEXT
    # ==========================
    return store_service.find_stores(location)


defined_tools = [
    search_products_tool,
    check_stock_tool,
    find_store_tool
]
