import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
import os
from urllib.parse import urljoin

# --- CẤU HÌNH ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7'
}


# --- HÀM HỖ TRỢ (UTILS) ---
def clean_text(text):
    """Làm sạch văn bản: xóa khoảng trắng thừa, xuống dòng"""
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()


def parse_price(price_str):
    """
    Chuyển đổi chuỗi giá '29.990.000₫' thành số nguyên 29990000.
    Hàm này được cải tiến để xử lý nhiều định dạng hơn.
    """
    if not price_str: return 0

    # Ưu tiên tìm chuỗi số có dấu chấm ngăn cách (ví dụ: 29.990.000)
    match = re.search(r'(\d{1,3}(?:\.\d{3})+)', price_str)
    if match:
        clean_str = re.sub(r'[^\d]', '', match.group(1))
        if clean_str:
            return int(clean_str)

    # Nếu không có, thử cách đơn giản là xóa hết ký tự không phải số
    clean_str = re.sub(r'[^\d]', '', price_str)
    try:
        price = int(clean_str)
        # Chỉ chấp nhận giá trị lớn hơn 100.000 để tránh nhầm lẫn với các số khác
        if price > 100000:
            return price
        return 0
    except (ValueError, TypeError):
        return 0


def extract_specs_dict(soup):
    """Lấy thông số kỹ thuật dưới dạng dictionary key-value từ nhiều cấu trúc web"""
    specs_dict = {}

    # Phương pháp cho CellphoneS
    if not specs_dict:
        tech_items = soup.select('.technical-content-item')
        if tech_items:
            for item in tech_items:
                title = item.select_one('.technical-content-item__title')
                content = item.select_one('.technical-content-item__content')
                if title and content:
                    key = clean_text(title.text)
                    value = clean_text(content.text)
                    if key and value:
                        specs_dict[key] = value

    # Phương pháp dự phòng chung (bảng)
    if not specs_dict:
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['th', 'td'])
                if len(cols) == 2:
                    key = clean_text(cols[0].text)
                    value = clean_text(cols[1].text)
                    if key and value:
                        specs_dict[key] = value

    return specs_dict


# --- LOGIC CRAWLER ---

def crawl_category(category_url):
    """
    Thu thập tất cả các link sản phẩm từ một trang danh mục.
    :param category_url: URL của trang danh mục
    :return: Một danh sách các URL sản phẩm đầy đủ.
    """
    print(f"🔎 Đang quét trang danh mục: {category_url}...")
    product_links = []
    try:
        response = requests.get(category_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ Lỗi {response.status_code} khi quét danh mục {category_url}")
            return []

        soup = BeautifulSoup(response.content, 'lxml')
        links = []

        # Sử dụng selector phù hợp cho từng trang
        if "cellphones.com.vn" in category_url:
            links = soup.select('div.product-info a.product__link')

        if not links:
            print("⚠️ Không tìm thấy link sản phẩm nào với các selector đã biết.")

        for link in links:
            href = link.get('href')
            if href and not href.startswith('http'):
                href = urljoin(category_url, href)
            if href:
                product_links.append(href)

        unique_links = sorted(list(set(product_links)))
        print(f"✅ Tìm thấy {len(unique_links)} link sản phẩm.")
        return unique_links

    except Exception as e:
        print(f"⚠️ Ngoại lệ khi quét danh mục: {e}")
        return []


def crawl_product(url):
    """
    Thu thập thông tin từ một URL sản phẩm.
    Hàm này có khả năng tách các phiên bản sản phẩm (VD: 256GB, 512GB)
    từ cùng một trang và lọc bỏ các sản phẩm không liên quan.
    :param url: URL của trang sản phẩm
    :return: Một danh sách các dictionary sản phẩm.
    """
    print(f"🔄 Đang xử lý: {url}...")
    try:
        time.sleep(random.uniform(1, 2))
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ Lỗi {response.status_code} khi truy cập {url}")
            return []

        soup = BeautifulSoup(response.content, 'lxml')

        # 1. Lấy thông tin chung và xác định TÊN SẢN PHẨM CỐT LÕI
        name_tag = soup.find('h1')
        base_name = clean_text(name_tag.text) if name_tag else "Không tên"

        # Loại bỏ dung lượng và các thông tin phụ để có tên gốc
        core_name = re.sub(r'\s*(\d+\s*(GB|TB)|\|.*$)', '', base_name, flags=re.IGNORECASE).strip()
        main_product_identifier = core_name

        specs_dict = extract_specs_dict(soup)

        desc_text = ""
        desc_div = soup.find('div', class_='card-content') or soup.find('div', class_='ksp-content')
        if desc_div:
            desc_text = clean_text(desc_div.get_text(separator=' ', strip=True))
        if len(desc_text) < 50:
            desc_text = ""

        category = "Điện thoại"
        name_lower = base_name.lower()
        url_lower = url.lower()
        laptop_keywords = ["laptop", "macbook", "strix", "rog", "vivobook", "zenbook"]
        if any(keyword in url_lower or keyword in name_lower for keyword in laptop_keywords):
            category = "Laptop"

        product_variations = []
        keys_to_remove_from_specs = []

        # 2. Tách các phiên bản sản phẩm
        if not product_variations:
            variation_container = soup.find('div', class_='box-content-group')
            if variation_container:
                items = variation_container.find_all('a', class_='item-child')
                for item in items:
                    name_div = item.find('div', class_='name')
                    price_p = item.find('p', class_='special-price')
                    if name_div and price_p:
                        variation_name = clean_text(name_div.text)
                        if main_product_identifier.lower() in variation_name.lower():
                            product_variations.append({
                                "name": variation_name,
                                "price_int": parse_price(price_p.text),
                            })

        # 3. Tạo danh sách sản phẩm cuối cùng
        final_products = []
        common_specs = specs_dict.copy()
        for key in set(keys_to_remove_from_specs):
            if key in common_specs:
                del common_specs[key]

        if product_variations:
            print(f"✅ Tìm thấy {len(product_variations)} phiên bản cho: {core_name}")
            for variation in product_variations:
                variation_specs = common_specs.copy()
                storage_match = re.search(r'(\d+\s*GB|\d+\s*TB)', variation["name"], re.IGNORECASE)
                if storage_match:
                    variation_specs["Bộ nhớ trong"] = storage_match.group(1).strip()

                final_products.append({
                    "url": url,
                    "name": variation["name"],
                    "price_int": variation["price_int"],
                    "category": category,
                    "specs": variation_specs,
                    "rag_content": f"Sản phẩm: {variation['name']}. Giá bán khoảng: {variation['price_int']:,} đồng. Cấu hình chi tiết: {json.dumps(variation_specs, ensure_ascii=False)}. Tính năng nổi bật: {desc_text}"
                })
        else:
            # Fallback: Nếu không có phiên bản, lấy giá chính của trang
            price_int = 0

            # CÁCH 1: Dựa vào gợi ý của bạn - tìm label và thẻ giá đi liền kề
            price_label = soup.find('div', class_='price-label')
            if price_label:
                next_element = price_label.find_next_sibling()
                if next_element:
                    price_int = parse_price(next_element.text)

            # CÁCH 2: Nếu cách trên không thành công, thử các selector CSS phổ biến
            if price_int == 0:
                price_selectors = [
                    '.box-info__box-price .product__price--show', # CellphoneS
                    '.product-price-current',                    # CellphoneS (dự phòng)
                    '.special-price',                            # CellphoneS (khuyến mãi)
                    '.style-price-special',                      # FPT Shop (khuyến mãi)
                    '.style-price',                              # FPT Shop (giá gốc)
                ]
                for selector in price_selectors:
                    price_tag = soup.select_one(selector)
                    if price_tag:
                        price_int = parse_price(price_tag.text)
                        if price_int > 0:
                            break

            if price_int > 0:
                print(f"✅ Thành công (1 sản phẩm): {base_name} - {price_int:,} đ")
            else:
                print(f"⚠️ Không tìm thấy giá cho: {base_name}. Thêm sản phẩm với giá 0.")

            final_products.append({
                "url": url,
                "name": base_name,
                "price_int": price_int,
                "category": category,
                "specs": common_specs,
                "rag_content": f"Sản phẩm: {base_name}. Giá bán khoảng: {price_int:,} đồng. Cấu hình chi tiết: {json.dumps(common_specs, ensure_ascii=False)}. Tính năng nổi bật: {desc_text}"
            })

        return final_products

    except Exception as e:
        print(f"⚠️ Ngoại lệ khi xử lý {url}: {e}")
        return []


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # URL mục tiêu là các trang danh mục sản phẩm
    category_urls = [
        "https://cellphones.com.vn/laptop/asus.html",

    ]

    all_product_links = []
    print("🚀 Bắt đầu quá trình khám phá link sản phẩm...")
    for cat_url in category_urls:
        links = crawl_category(cat_url)
        if links:
            all_product_links.extend(links)

    unique_product_links = sorted(list(set(all_product_links)))
    print(f"\n➡️ Tổng cộng sẽ thu thập dữ liệu từ {len(unique_product_links)} sản phẩm.")

    crawled_data = []
    print("\n🚀 Bắt đầu quá trình thu thập dữ liệu chi tiết...")

    for link in unique_product_links:
        products = crawl_product(link)
        if products:
            crawled_data.extend(products)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, 'data', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'products.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(crawled_data, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Hoàn tất! Dữ liệu đã được lưu tại:\n{output_file}")
    print(f"Tổng số sản phẩm đã thu thập: {len(crawled_data)}")
