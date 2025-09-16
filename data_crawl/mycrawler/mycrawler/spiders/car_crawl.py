import scrapy
import pymysql
import os
from dotenv import load_dotenv
from mycrawler.items import CarItem
import re

load_dotenv()

class CarCrawlSpider(scrapy.Spider):
    name = "car_crawl"
    allowed_domains = ["bonbanh.com"]

    def start_requests(self):
        # kết nối mysql để lấy link
        conn = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            charset="utf8mb4",
            use_unicode=True,
            cursorclass=pymysql.cursors.DictCursor,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT link FROM car_links WHERE crawled = 0")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            yield scrapy.Request(url=row["link"], callback=self.parse_car)

    def parse_car(self, response):
        item = CarItem()

        # Tên & giá
        title_text = response.css("h1::text").get()
        if title_text:
            # Làm sạch xuống dòng, tab, nhiều khoảng trắng
            clean_title = " ".join(title_text.split())
            # Bỏ chữ "Xe " ở đầu nếu có
            clean_title = re.sub(r"^Xe\s+", "", clean_title, flags=re.IGNORECASE)

            # Tách phần giá: thường nằm sau dấu '-' hoặc cuối cùng có chữ 'Triệu', 'Tỷ'
            match = re.search(r"[-–]\s*([\d\.]+(?:\s*Triệu|\s*Tỷ))", clean_title)
            if match:
                item["price"] = match.group(1).strip()
                # Bỏ phần giá ra khỏi tên
                name_part = clean_title[:match.start()].strip()
                item["name"] = name_part
            else:
                # Không tìm thấy giá
                item["name"] = clean_title
                item["price"] = None

        # Tách brand và model từ name nếu có
        breadcrumb = response.css("span[itemprop='name'] strong::text").getall()
        if len(breadcrumb) >= 2:
            item["brand"] = breadcrumb[0].strip()   # Toyota
            item["model"] = breadcrumb[1].strip()   # Innova
        else:
            item["brand"] = None
            item["model"] = None

        # Ngày đăng
        date_text = response.css("div.notes::text").get()
        clean_text = " ".join(date_text.split())
        post_date = None  # gán mặc định để tránh lỗi
        if date_text:
            match = re.search(r"(\d{2}/\d{2}/\d{4})", clean_text)
            if match:
                post_date = match.group(1)

        item["date_posted"] = post_date

        # Hàm extract_info lấy từ dict specs đã parse trước
        def extract_info(label, specs):
            return specs.get(label, None)


        # Parse toàn bộ thông số
        specs = {}
        rows = response.css("div#mail_parent.row, div#mail_parent.row_last")

        for row in rows:
            key = row.css("div.label label::text").get(default="").strip().replace(":", "")
            value = row.css("div.txt_input span::text, div.inputbox span::text").get(default="").strip()
            if key and value:
                specs[key] = value

        # Gán vào item
        item["year"] = extract_info("Năm sản xuất", specs)
        item["car_condition"] = extract_info("Tình trạng", specs)
        item["mileage"] = extract_info("Số Km đã đi", specs)
        item["origin"] = extract_info("Xuất xứ", specs)
        item["body_style"] = extract_info("Kiểu dáng", specs)
        item["transmission"] = extract_info("Hộp số", specs)
        item["engine"] = extract_info("Động cơ", specs)
        item["exterior_color"] = extract_info("Màu ngoại thất", specs)
        item["interior_color"] = extract_info("Màu nội thất", specs)
        item["seats"] = extract_info("Số chỗ ngồi", specs)
        item["doors"] = extract_info("Số cửa", specs)
        item["drivetrain"] = extract_info("Dẫn động", specs)

        # thông tin người bán
        contact_box = response.css("div.contact-box")
        item["seller_name"] = contact_box.css("a.cname::text, span.cname::text").get(default="").strip()

        phone = contact_box.css("span.cphone a::text").get()
        # Trường hợp 2 & 3: text trực tiếp trong span (bỏ script)
        if not phone:
            # Lấy tất cả text trong span.cphone (bao gồm cả sau script)
            phone_texts = contact_box.css("span.cphone ::text").getall()
            # Loại bỏ chuỗi rỗng và strip
            phone_texts = [t.strip() for t in phone_texts if t.strip()]
            joined_text = " ".join(phone_texts)

            # Regex bắt chuỗi dạng số điện thoại Việt Nam
            match = re.search(r"\d{2,4}[\s\-]?\d{3}[\s\-]?\d{3,4}", joined_text)
            if match:
                phone = match.group(0)

        item["seller_phone"] = phone
        # Địa chỉ nằm ở ngay sau text "Địa chỉ:" trong contact-txt
        # Có thể lấy cả đoạn text rồi lọc ra
        contact_texts = contact_box.css("div.contact-txt::text").getall()
        contact_texts = [t.strip() for t in contact_texts if t.strip()]

        # Tìm text bắt đầu bằng "Địa chỉ:"
        address = next((t.replace("Địa chỉ:", "").strip() for t in contact_texts if "Địa chỉ:" in t), None)

        item["seller_address"] = address
        print(item)
        
        yield item





# contact_box = response.css("div.contact-box")
# item["seller_name"] = contact_box.css("a.cname::text, span.cname::text").get(default="").strip()

# phone = contact_box.css("span.cphone a::text").get()
# # Trường hợp 2 & 3: text trực tiếp trong span (bỏ script)
# if not phone:
#     # Lấy tất cả text trong span.cphone (bao gồm cả sau script)
#     phone_texts = contact_box.css("span.cphone ::text").getall()
#     # Loại bỏ chuỗi rỗng và strip
#     phone_texts = [t.strip() for t in phone_texts if t.strip()]
#     joined_text = " ".join(phone_texts)

#     # Regex bắt chuỗi dạng số điện thoại Việt Nam
#     match = re.search(r"\d{2,4}[\s\-]?\d{3}[\s\-]?\d{3,4}", joined_text)
#     if match:
#         phone = match.group(0)

# item["seller_phone"] = phone
# # item["seller_phone"] = contact_box.css("span.cphone ::text").get(default="").strip()
# # item["seller_phone"] = contact_box.css("span.cphone a::text").get(default="").strip()
# contact_texts = contact_box.css("div.contact-txt::text").getall()
# contact_texts = [t.strip() for t in contact_texts if t.strip()]
# address = next((t.replace("Địa chỉ:", "").strip() for t in contact_texts if "Địa chỉ:" in t), None)
# item["seller_address"] = address
# print(item)


# if title_text:
#     clean_title = " ".join(title_text.split())
#     if "-" in clean_title:
#         item["name"], item["price"] = [x.strip() for x in clean_title.replace("Xe", "", 1).split("-", 1)]
#     else:
#         item["name"] = clean_title
#         item["price"] = None