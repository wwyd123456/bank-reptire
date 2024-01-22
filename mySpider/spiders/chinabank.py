import scrapy
from  mySpider.items import MyspiderItem
from scrapy.http import Request
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

class ChinaBankSpider(scrapy.Spider):
    name = 'chinabank'
    allowed_domains = ["www.boc.cn/sourcedb/whpj/"]
    # start_urls = (
    #     "http://www.boc.cn/sourcedb/whpj/",
    # )
    def __init__(self, date=None, name=None,*args, **kwargs):
        super(ChinaBankSpider, self).__init__(*args, **kwargs)
        self.date = date
        self.name = name

    def start_requests(self):
        url = f"http://www.boc.cn/sourcedb/whpj/"
        yield Request(url=url, callback=self.parse,meta={"date":self.date,"name":self.name})

    def parse(self,response):
        item = MyspiderItem()
        r = response.css("table .odd td:nth-last-child(2)").extract()
        price = r[0][4:10]
        item["price"] = price
        yield item
