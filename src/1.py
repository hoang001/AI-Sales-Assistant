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
    """
    Dọn dẹp chuỗi bằng cách loại bỏ khoảng trắng và ký tự xuống dòng thừa.

    Args:
        text (str): Chuỗi đầu vào cần làm sạch.

    Returns:
        str: Chuỗi đã được làm sạch, chỉ có một khoảng trắng giữa các từ.
    """
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()


def parse_price(price_str):
    """
    Chuyển đổi chuỗi giá có định dạng (ví dụ: '29.990.000₫') thành một số nguyên.

    Hàm này được thiết kế để xử lý nhiều định dạng giá khác nhau, ưu tiên tìm
    các số được phân tách bằng dấu chấm, sau đó mới loại bỏ tất cả các ký tự
    không phải là số. Nó cũng lọc bỏ các số nhỏ để tránh phân tích sai giá trị.

    Args:
        price_str (str): Chuỗi chứa thông tin giá.

    Returns:
        int: Giá đã được phân tích dưới dạng số nguyên, hoặc 0 nếu phân tích
             thất bại hoặc giá không hợp lệ (ví dụ: nhỏ hơn 100,000).
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
    """
    Trích xuất thông số kỹ thuật từ đối tượng BeautifulSoup thành một dictionary.

    Hàm cố gắng tìm thông số kỹ thuật bằng nhiều phương pháp để hỗ trợ các cấu
    trúc website khác nhau, bắt đầu với các selector dành riêng cho CellphoneS
    và sau đó chuyển sang các bảng HTML chung.

    Args:
        soup (BeautifulSoup): Đối tượng BeautifulSoup của trang sản phẩm.

    Returns:
        dict: Một dictionary với key là tên thông số (ví dụ: "CPU") và
              value là chi tiết tương ứng.
    """
    specs_dict = {}

    # Phương pháp cho CellphoneS
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
    Quét một trang danh mục để thu thập tất cả các liên kết sản phẩm duy nhất.

    Args:
        category_url (str): URL của trang danh mục cần quét.

    Returns:
        list[str]: Một danh sách đã được sắp xếp gồm các URL tuyệt đối, duy nhất
                   của các sản phẩm được tìm thấy. Trả về danh sách rỗng nếu thất bại.
    """
    print(f"Đang quét trang danh mục: {category_url}...")
    product_links = []
    try:
        response = requests.get(category_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"Lỗi {response.status_code} khi quét danh mục {category_url}")
            return []

        soup = BeautifulSoup(response.content, 'lxml')
        links = soup.select('div.product-info a.product__link')

        if not links:
            print("Không tìm thấy link sản phẩm nào với các selector đã biết.")

        for link in links:
            href = link.get('href')
            if href and not href.startswith('http'):
                href = urljoin(category_url, href)
            if href:
                product_links.append(href)

        unique_links = sorted(list(set(product_links)))
        print(f"Tìm thấy {len(unique_links)} link sản phẩm.")
        return unique_links

    except Exception as e:
        print(f"Ngoại lệ khi quét danh mục: {e}")
        return []


def crawl_product(url):
    """
    Quét một trang sản phẩm duy nhất để trích xuất thông tin chi tiết.

    Hàm này xử lý các trang có thể chứa nhiều phiên bản sản phẩm (ví dụ: dung
    lượng lưu trữ hoặc màu sắc khác nhau). Nó trích xuất các chi tiết chung như
    thông số kỹ thuật và mô tả, sau đó xác định từng phiên bản với tên và giá
    cụ thể.

    Args:
        url (str): URL của trang sản phẩm.

    Returns:
        list[dict]: Một danh sách các dictionary, mỗi dictionary đại diện cho
                    một phiên bản sản phẩm duy nhất. Trả về danh sách rỗng nếu
                    không thể xử lý trang hoặc không tìm thấy giá hợp lệ.
    """
    print(f"Đang xử lý: {url}...")
    try:
        time.sleep(random.uniform(1, 2))
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"Lỗi {response.status_code} khi truy cập {url}")
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
        tablet_keywords = ["tablet", "ipad", "tab"]
        smartwatch_keywords = ["watch", "đồng hồ"]

        if any(keyword in url_lower or keyword in name_lower for keyword in laptop_keywords):
            category = "Laptop"
        elif any(keyword in url_lower or keyword in name_lower for keyword in tablet_keywords):
            category = "Tablet"
        elif any(keyword in url_lower or keyword in name_lower for keyword in smartwatch_keywords):
            category = "Đồng hồ thông minh"

        product_variations = []
        keys_to_remove_from_specs = []

        # 2. Tách các phiên bản sản phẩm
        # CÁCH 1: Từ bảng thông số (cho sản phẩm sắp ra mắt)
        variations_dict = {}
        for key, value in specs_dict.items():
            price_from_value = parse_price(value)
            if main_product_identifier.lower() in key.lower() and price_from_value > 0:
                normalized_name = clean_text(key)
                normalized_name = re.sub(r'^(Giá|Giá dự kiến|Phiên bản)\s+', '', normalized_name,
                                         flags=re.IGNORECASE).strip()
                normalized_name = re.sub(r'\s*\|.*$', '', normalized_name).strip()

                if normalized_name not in variations_dict:
                    variations_dict[normalized_name] = {
                        "name": normalized_name,
                        "price_int": price_from_value,
                    }
                keys_to_remove_from_specs.append(key)

        if variations_dict:
            product_variations = list(variations_dict.values())

        # CÁCH 2: Từ box chọn phiên bản (cho sản phẩm thông thường)
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
                            variation_price = parse_price(price_p.text)
                            if variation_price > 0:
                                product_variations.append({
                                    "name": variation_name,
                                    "price_int": variation_price,
                                })

        # 3. Tạo danh sách sản phẩm cuối cùng
        final_products = []
        common_specs = specs_dict.copy()
        for key in set(keys_to_remove_from_specs):
            if key in common_specs:
                del common_specs[key]

        if product_variations:
            print(f"Tìm thấy {len(product_variations)} phiên bản cho: {core_name}")
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
            price_label = soup.find('div', class_='price-label')
            if price_label:
                next_element = price_label.find_next_sibling()
                if next_element:
                    price_int = parse_price(next_element.text)

            if price_int == 0:
                price_selectors = [
                    '.box-info__box-price .product__price--show',
                    '.product-price-current',
                    '.special-price',
                ]
                for selector in price_selectors:
                    price_tag = soup.select_one(selector)
                    if price_tag:
                        price_int = parse_price(price_tag.text)
                        if price_int > 0:
                            break

            # Chỉ thêm sản phẩm vào danh sách nếu tìm thấy giá hợp lệ
            if price_int > 0:
                print(f"Thành công (1 sản phẩm): {base_name} - {price_int:,} đ")
                final_products.append({
                    "url": url,
                    "name": base_name,
                    "price_int": price_int,
                    "category": category,
                    "specs": common_specs,
                    "rag_content": f"Sản phẩm: {base_name}. Giá bán khoảng: {price_int:,} đồng. Cấu hình chi tiết: {json.dumps(common_specs, ensure_ascii=False)}. Tính năng nổi bật: {desc_text}"
                })
            else:
                print(f"Không tìm thấy giá cho: {base_name}. Bỏ qua sản phẩm này.")

        return final_products

    except Exception as e:
        print(f"Ngoại lệ khi xử lý {url}: {e}")
        return []


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Danh sách các URL danh mục cần quét
    category_urls = [
                #DIEN_THOAI
        "https://cellphones.com.vn/mobile/apple/iphone-17.html",
        "https://cellphones.com.vn/mobile/apple/iphone-air.html",
        "https://cellphones.com.vn/mobile/apple/iphone-16.html",
        "https://cellphones.com.vn/mobile/apple/iphone-15.html",
        "https://cellphones.com.vn/mobile/apple/iphone-14.html",
        "https://cellphones.com.vn/mobile/apple/iphone-13.html",
        "https://cellphones.com.vn/mobile/samsung/galaxy-s.html",
        "https://cellphones.com.vn/mobile/samsung/galaxy-a.html",
        "https://cellphones.com.vn/mobile/samsung/galaxy-m.html",
        "https://cellphones.com.vn/mobile/samsung/galaxy-z.html",
        "https://cellphones.com.vn/mobile/xiaomi/15-series.html",
        "https://cellphones.com.vn/mobile/xiaomi/14-series.html",
        "https://cellphones.com.vn/mobile/xiaomi/13-series.html",
        "https://cellphones.com.vn/mobile/xiaomi/12-series.html",
        "https://cellphones.com.vn/mobile/xiaomi/redmi.html",
        "https://cellphones.com.vn/mobile/pocophone.html",
        "https://cellphones.com.vn/mobile/oppo/a-series.html",
        "https://cellphones.com.vn/mobile/oppo/find-x-series.html",
        "https://cellphones.com.vn/mobile/oppo/find-n-series.html",
        "https://cellphones.com.vn/mobile/oppo/reno-series.html",
        "https://cellphones.com.vn/mobile/vivo/y-series.html",
        "https://cellphones.com.vn/mobile/vivo/v-series.html",
        "https://cellphones.com.vn/mobile/vivo/x-series.html",
        "https://cellphones.com.vn/mobile/realme/c-series.html",
        "https://cellphones.com.vn/mobile/honor.html",
        "https://cellphones.com.vn/mobile/tecno.html",
        "https://cellphones.com.vn/mobile/nubia.html",
        "https://cellphones.com.vn/mobile/sony.html",
        "https://cellphones.com.vn/mobile/infinix.html",

        #TAPLET
        "https://cellphones.com.vn/tablet/ipad-pro.html",
        "https://cellphones.com.vn/tablet/ipad-air.html",
        "https://cellphones.com.vn/tablet/ipad-mini.html",
        "https://cellphones.com.vn/tablet/ipad-10-2.html",
        "https://cellphones.com.vn/tablet/ipad-10-9.html",
        "https://cellphones.com.vn/tablet/samsung/samsung-galaxy-tab-s11-series.html",
        "https://cellphones.com.vn/tablet/samsung/samsung-galaxy-tab-s10-series.html",
        "https://cellphones.com.vn/tablet/samsung/samsung-galaxy-tab-s9-series.html",
        "https://cellphones.com.vn/tablet/xiaomi.html",
        "https://cellphones.com.vn/tablet/huawei.html",
        "https://cellphones.com.vn/tablet/lenovo.html",
        "https://cellphones.com.vn/tablet/teclast.html",
        "https://cellphones.com.vn/tablet/honor.html",

        #LAPTOP
        "https://cellphones.com.vn/laptop/mac/macbook-air.html",
        "https://cellphones.com.vn/laptop/mac/macbook-pro.html",
        "https://cellphones.com.vn/laptop/mac/mini.html",
        "https://cellphones.com.vn/laptop/mac/mac-studio.html",
        "https://cellphones.com.vn/laptop/mac/imac.html",
        "https://cellphones.com.vn/laptop/asus/vivobook.html",
        "https://cellphones.com.vn/laptop/asus/gaming.html",
        "https://cellphones.com.vn/laptop/asus/zenbook.html",
        "https://cellphones.com.vn/laptop/asus/expertbook.html",
        "https://cellphones.com.vn/laptop/asus/rog.html",
        "https://cellphones.com.vn/laptop/asus/tuf.html",
        "https://cellphones.com.vn/laptop/lenovo/ideapad.html",
        "https://cellphones.com.vn/laptop/lenovo/thinkpad.html",
        "https://cellphones.com.vn/laptop/lenovo/yoga.html",
        "https://cellphones.com.vn/laptop/lenovo/thinkbook.html",
        "https://cellphones.com.vn/laptop/lenovo/v-series.html",
        "https://cellphones.com.vn/laptop/lenovo/loq.html",
        "https://cellphones.com.vn/laptop/lenovo/legion.html",
        "https://cellphones.com.vn/laptop/msi/modern.html",
        "https://cellphones.com.vn/laptop/msi/prestige.html",
        "https://cellphones.com.vn/laptop/msi/gf-series.html",
        "https://cellphones.com.vn/laptop/msi/cyborg.html",
        "https://cellphones.com.vn/laptop/msi/katana.html",
        "https://cellphones.com.vn/laptop/msi/venture.html",
        "https://cellphones.com.vn/laptop/acer/nitro.html",
        "https://cellphones.com.vn/laptop/acer/aspire.html",
        "https://cellphones.com.vn/laptop/acer/swift.html",
        "https://cellphones.com.vn/laptop/acer/predator.html",
        "https://cellphones.com.vn/laptop/hp/pavilion.html",
        "https://cellphones.com.vn/laptop/hp/victus.html",
        "https://cellphones.com.vn/laptop/hp/envy.html",
        "https://cellphones.com.vn/laptop/hp/compaq.html",
        "https://cellphones.com.vn/laptop/hp/spectre.html",
        "https://cellphones.com.vn/laptop/hp/omnibook.html",
        "https://cellphones.com.vn/laptop/dell/inspiron.html",
        "https://cellphones.com.vn/laptop/dell/vostro.html",
        "https://cellphones.com.vn/laptop/dell/xps.html",
        "https://cellphones.com.vn/laptop/dell/latitude.html",
        "https://cellphones.com.vn/laptop/dell/dell-15.html",
        "https://cellphones.com.vn/laptop/lg.html",
        "https://cellphones.com.vn/laptop/gigabyte.html",
        "https://cellphones.com.vn/laptop/masstel.html",
        "https://cellphones.com.vn/laptop/samsung.html",

        #DONG_HO_THONG_MINH
        "https://cellphones.com.vn/do-choi-cong-nghe/apple-watch/series-11.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/apple-watch/series-10.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/apple-watch/ultra-3.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/apple-watch/ultra.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/apple-watch/se-3.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/apple-watch/se.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/samsung.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/xiaomi.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/huawei.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/coros.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/garmin.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/amazfit.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/kieslect.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/soundpeats.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/black-shark.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/masstel.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/myalo.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/mibro.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/viettel.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/kospet.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/imoo.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/goly.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/kavvo.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/riversong.html",
        "https://cellphones.com.vn/do-choi-cong-nghe/wonlex.html",
    ]

    # Bước 1: Khám phá tất cả các link sản phẩm từ các trang danh mục
    all_product_links = []
    print("Bắt đầu quá trình khám phá link sản phẩm...")
    for cat_url in category_urls:
        links = crawl_category(cat_url)
        if links:
            all_product_links.extend(links)

    unique_product_links = sorted(list(set(all_product_links)))
    print(f"\nTổng cộng sẽ thu thập dữ liệu từ {len(unique_product_links)} sản phẩm.")

    # Bước 2: Quét từng link sản phẩm để lấy dữ liệu chi tiết
    crawled_data = []
    print("\nBắt đầu quá trình thu thập dữ liệu chi tiết...")

    for link in unique_product_links:
        products = crawl_product(link)
        if products:
            crawled_data.extend(products)

    # Bước 3: Khử trùng lặp kết quả dựa trên tên sản phẩm đã chuẩn hóa
    print("\nBắt đầu quá trình khử trùng lặp sản phẩm...")
    final_unique_products = []
    seen_product_names = set()
    for product in crawled_data:
        product_name = product.get("name", "")
        # Chuẩn hóa tên để xử lý các hậu tố như "| Chính hãng"
        normalized_name = re.sub(r'\s*\|.*$', '', product_name).strip()
        if normalized_name and normalized_name not in seen_product_names:
            final_unique_products.append(product)
            seen_product_names.add(normalized_name)

    if len(crawled_data) > len(final_unique_products):
        print(f"Đã loại bỏ {len(crawled_data) - len(final_unique_products)} sản phẩm trùng lặp.")

    # Bước 4: Lưu dữ liệu cuối cùng vào file JSON
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, 'data', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'products.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_unique_products, f, ensure_ascii=False, indent=2)

    print(f"\nHoàn tất! Dữ liệu đã được lưu tại:\n{output_file}")
    print(f"Tổng số sản phẩm đã thu thập: {len(final_unique_products)}")
