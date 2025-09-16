import scrapy
from crawl_link.items import CrawlLinkItem


class LinkSpider(scrapy.Spider):
    name = "link_spider"
    allowed_domains = ["bonbanh.com"]
    start_urls = ["https://bonbanh.com/oto"]

    # cho phép truyền tham số từ command line
    def __init__(self, start_page=1, end_page=10, *args, **kwargs):
        super(LinkSpider, self).__init__(*args, **kwargs)
        self.start_page = int(start_page)
        self.end_page = int(end_page)
        self.current_page = self.start_page

    def start_requests(self):
        url = f"https://bonbanh.com/oto/page,{self.start_page}"
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        # lấy link chi tiết
        for href in response.css("li.car-item a[itemprop='url']::attr(href)").getall():
            item = CrawlLinkItem()
            item["link"] = response.urljoin(href)
            yield item

        # phân trang có kiểm soát
        if self.current_page < self.end_page:
            self.current_page += 1
            next_url = f"https://bonbanh.com/oto/page,{self.current_page}"
            yield scrapy.Request(next_url, callback=self.parse)
