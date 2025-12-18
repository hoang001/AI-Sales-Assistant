# tools.py

# ⚠️ store_service sẽ được inject từ main.py
store_service = None


def init_tools(service):
    global store_service
    store_service = service


def search_products_tool(query: str):
    """Tìm kiếm sản phẩm, xem hình ảnh và giá khuyến mãi."""
    if not store_service:
        return "⚠️ Hệ thống chưa sẵn sàng."
    return store_service.search_products(query)


def check_stock_tool(product_name: str):
    """Kiểm tra tồn kho và giá chính xác."""
    if not store_service:
        return "⚠️ Hệ thống chưa sẵn sàng."
    return store_service.check_stock(product_name)


def find_store_tool(location: str):
    """
    Tìm cửa hàng CellphoneS gần nhất.

    - GPS → dùng trực tiếp
    - Text → Geocode → Places
    """
    if not store_service:
        return "<div class='error-message'>⚠️ Hệ thống chưa sẵn sàng.</div>"

    # ==========================
    # TRƯỜNG HỢP GPS
    # ==========================
    if isinstance(location, str) and location.startswith("GPS:"):
        try:
            _, coords = location.split("GPS:")
            lat_str, lng_str = coords.split(",")
            lat = float(lat_str.strip())
            lng = float(lng_str.strip())

            return store_service.find_nearest_store(lat, lng)

        except Exception as e:
            return f"<div class='error-message'>❌ Lỗi GPS: {e}</div>"

    # ==========================
    # TRƯỜNG HỢP TEXT
    # ==========================
    try:
        lat, lng = store_service.geocode_location(location)
        return store_service.find_nearest_store(lat, lng)

    except Exception as e:
        return f"<div class='error-message'>❌ Lỗi tìm địa điểm: {e}</div>"


defined_tools = [
    search_products_tool,
    check_stock_tool,
    find_store_tool
]
