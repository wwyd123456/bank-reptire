# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import scrapy
from selenium import webdriver
from retrying import retry
from selenium.webdriver.common.keys import Keys

class MyspiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MyspiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)




# 驱动selenium中间件
class SeleniumMiddleware(object):
    def __init__(self, *args, **kwargs):
        self.driver = webdriver.Chrome()

    # 总共重试40次，每次间隔100毫秒
    @retry(stop_max_attempt_number=40, wait_fixed=1000)
    def retry_load_page(self, request, spider):
        # 如果页面数据找到了，表示网页渲染成功，程序正常向下执行
        try:
            # 根据页面有无//h2节点，来判断网页是否加载成功
            self.driver.find_element_by_xpath("//h2")
        except:
            self.count += 1
            spider.logger.info("<{}> retry {} times".format(request.url, self.count))
            # 手动抛出异常交给retry捕获，这样retry才能正常工作
            raise Exception("<{}> page load failed.".format(request.url))

    def process_request(self, request, spider):
        self.count = 0
        self.driver.get(request.url)
        # 显示等待
        # time.sleep(2) 
        try:
            self.retry_load_page(request, spider)
            # 隐式等待
            # 判断页面数据是否渲染成功，如果没成功继续等待，如果成功提取数据不用等待。
            # Unicode 字符串
            input = self.driver.find_element_by_id("nothing")
            input.send_keys(request.meta["date"])
            input.send_keys(Keys.RETURN)
            option = self.driver.find_element_by_id("pjname")
            option.send_keys(request.meta["name"])
            option.send_keys(Keys.RETURN)
            searchbutton = self.driver.find_elements_by_css_selector("tbody .search_btn")[0]
            searchbutton.click()
            html = self.driver.page_source
            # 返回一个response响应对象给引擎，引擎会认为是下载器返回的响应，默认交给spider解析
            return scrapy.http.HtmlResponse(url=self.driver.current_url, body=html.encode("utf-8"),
                                            encoding="utf-8", request=request)

        except Exception as e:
            spider.logger.error(e)
            return request
