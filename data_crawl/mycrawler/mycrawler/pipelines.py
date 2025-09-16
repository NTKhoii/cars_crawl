# mycrawler/pipelines.py
import os
from dotenv import load_dotenv
import pymysql
from scrapy.exceptions import DropItem

# Tự động load file .env ở thư mục chạy (nếu .env nằm ở project root)
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
            use_unicode=True,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        self.cursor = self.conn.cursor()
        # tạo table nếu cần
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            price VARCHAR(100),
            brand VARCHAR(100),
            model VARCHAR(100),
            date_posted VARCHAR(50),
            year VARCHAR(10),
            car_condition VARCHAR(50),
            mileage VARCHAR(50),
            origin VARCHAR(50),
            body_style VARCHAR(50),
            transmission VARCHAR(50),
            engine VARCHAR(50),
            exterior_color VARCHAR(50),
            interior_color VARCHAR(50),
            seats VARCHAR(10),
            doors VARCHAR(10),
            drivetrain VARCHAR(50),
            seller_name VARCHAR(100),
            seller_phone VARCHAR(50),
            seller_address TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        self.conn.commit()

    def process_item(self, item, spider):
        try:
            self.cursor.execute("""
                INSERT INTO cars (
                    name, price, brand, model, date_posted, year, car_condition, mileage,
                    origin, body_style, transmission, engine, exterior_color,
                    interior_color, seats, doors, drivetrain, seller_name, seller_phone, seller_address
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item.get("name"), item.get("price"), item.get("brand"), item.get("model"), item.get("date_posted"),
                item.get("year"), item.get("car_condition"), item.get("mileage"),
                item.get("origin"), item.get("body_style"), item.get("transmission"),
                item.get("engine"), item.get("exterior_color"), item.get("interior_color"),
                item.get("seats"), item.get("doors"), item.get("drivetrain"),
                item.get("seller_name"), item.get("seller_phone"), item.get("seller_address")
            ))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise DropItem(f"DB insert error: {e}")
        return item

    def close_spider(self, spider):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception:
            pass
