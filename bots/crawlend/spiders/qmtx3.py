from scrapy.spider import CrawlSpider
from bots.crawlend.items import CrawlendItem
import scrapy
from bs4 import BeautifulSoup
import requests


class TestSpider(CrawlSpider):
    name = "qmtx3"
    start_urls = ['http://www.qmtx3.com/']

    def get_menus(self, response):
        res = BeautifulSoup(response.text, 'lxml').find("div", {"class": "nav"})
        menus = res.find_all('a')
        menus_list = []
        for menu in menus:
            menus_list.append(menu['href'])
            print(menu)
        return menus_list

    def parse(self, response):
        self.get_menus(response)
            # print(tag_a)
            # print(tag_a['href'])
            # print(tag_a.get_text)
