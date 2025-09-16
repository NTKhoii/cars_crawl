# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# file chứa định nghĩa các item để lưu trữ dữ liệu crawl được

import scrapy

class CarItem(scrapy.Item):
    # Thông tin cơ bản
    name = scrapy.Field()
    brand = scrapy.Field()
    model = scrapy.Field()
    price = scrapy.Field()
    date_posted = scrapy.Field()
    
    # Thông số kỹ thuật
    year = scrapy.Field()
    car_condition = scrapy.Field()
    mileage = scrapy.Field()
    origin = scrapy.Field()
    body_style = scrapy.Field()
    transmission = scrapy.Field()
    engine = scrapy.Field()
    exterior_color = scrapy.Field()
    interior_color = scrapy.Field()
    seats = scrapy.Field()
    doors = scrapy.Field()
    drivetrain = scrapy.Field()

    # Liên hệ
    seller_name = scrapy.Field()
    seller_phone = scrapy.Field()
    seller_address = scrapy.Field()