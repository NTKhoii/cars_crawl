import os
import pymysql
from dotenv import load_dotenv
from scrapy.exceptions import DropItem

# Load biến môi trường từ file .env (ở project root)
load_dotenv()

class MySQLPipeline:

    def open_spider(self, spider):
        host = os.getenv("MYSQL_HOST", "localhost")
        port = int(os.getenv("MYSQL_PORT", 3306))
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        database = os.getenv("MYSQL_DATABASE")

        self.conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        self.cursor = self.conn.cursor()

        # Tạo bảng nếu chưa có
        create_table_query = """
        CREATE TABLE IF NOT EXISTS car_links (
            id INT AUTO_INCREMENT PRIMARY KEY,
            link VARCHAR(500) UNIQUE,
            crawled TINYINT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()   # ✅ dùng self.conn thay vì self.connection

    def close_spider(self, spider):
        # Đóng kết nối khi spider kết thúc
        if hasattr(self, "cursor"):
            self.cursor.close()
        if hasattr(self, "conn"):
            self.conn.close()

    def process_item(self, item, spider):
        link = item.get("link")
        if not link:
            raise DropItem("Missing link in item")

        try:
            insert_query = "INSERT IGNORE INTO car_links (link) VALUES (%s)"
            self.cursor.execute(insert_query, (link,))
            self.conn.commit()
        except Exception as e:
            spider.logger.error(f"MySQL insert error: {e}")
            raise DropItem(f"MySQL insert error: {e}")

        return item
