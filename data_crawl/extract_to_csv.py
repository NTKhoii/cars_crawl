import pandas as pd
from sqlalchemy import create_engine

# Tạo engine kết nối MySQL
engine = create_engine("mysql+pymysql://admin:admin123@localhost:3306/old_car_db?charset=utf8mb4")

# Đọc dữ liệu
df = pd.read_sql("SELECT * FROM cars", engine)

# Xuất ra CSV với UTF-8
df.to_csv("cars_2.csv", index=False, encoding="utf-8-sig")
