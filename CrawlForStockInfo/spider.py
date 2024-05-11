import scrapy
from scrapy_selenium import SeleniumRequest
# from fake_useragent import UserAgent
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from items import StockInfoItem


class TestforstockinfoSpider(scrapy.Spider):
    name = "testForStockInfo"
    head = {
            'content-type': 'text/html; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }

    def start_requests(self):
        url = "https://baike.baidu.com/wikitag/taglist?tagId=62991"

        yield SeleniumRequest(url=url,
                              headers=self.head,
                              callback=self.parse,
                              wait_time=10,
                              wait_until=EC.presence_of_all_elements_located((By.CLASS_NAME, "waterFall_item"))
                            )

    def parse(self, response):  # HtmlResponse
        driver = response.request.meta["driver"]  # Use like python native selenium.
        driver.maximize_window()

        new_element_locator = (By.CLASS_NAME, 'waterFall_item')
        elements = driver.find_elements(*new_element_locator)
        
        page_size = 0
        for i in range(page_size):
            # 滾動到頁面底部
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            num_loaded_elements = len(elements)
            WebDriverWait(driver, 10).until(
                lambda driver: len(driver.find_elements(*new_element_locator)) > num_loaded_elements
            )
            elements = driver.find_elements(*new_element_locator)

        # elements_div = driver.find_elements(By.CLASS_NAME, 'waterFall_item')
        for element in elements:
            href = element.find_element(By.TAG_NAME, 'a').get_attribute('href')
            yield scrapy.Request(url=href,
                                 headers=self.head,
                                 callback=self.parseEveryPage
                                )

    def parseEveryPage(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')

        stockItem = StockInfoItem()

        stockItem['url'] = response.url
        content = soup.find(class_='J-lemma-content')
        if content:
            stockItem['title'] = soup.find(class_='J-lemma-title').get_text()
            stockItem['content'] = content.get_text()
        else:
            stockItem['title'] = None
            stockItem['content'] = '錯誤找不到class=J-lemma-content'
        
        yield stockItem

    # locator = (By.CLASS_NAME, "waterFall_item ")  # 定位器
    # def explictWait(self, driver, locator, timeout=10):
    #     # 等待新元素加載
    #     search_input = WebDriverWait(driver, timeout).until(
    #         EC.presence_of_element_located(locator)
    #     )