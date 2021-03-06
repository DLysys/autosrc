import scrapy
from bs4 import BeautifulSoup
from apps.companies.models import Book
import requests


class A52qlgSpider(scrapy.Spider):
    name = '52qlg'
    allowed_domains = ['52qlg.com']
    root_url = 'http://www.52qlg.com/list/'
    start_urls = ['http://www.52qlg.com/list/list_2_1.html']

    def parse(self, response):
        res = BeautifulSoup(response.text, 'lxml').find("div", {"class": "listl list2"})
        titles = res.find_all('h3')
        for t in titles:
            # item = CrawlendItem()
            # item['title'] = t.find('a').get_text()
            # item['author'] = 1
            # item[''] = t.find('a')['href']
            # yield item
            title = t.find('a').get_text()
            url = t.find('a')['href']
            html = requests.get(url)
            res2 = BeautifulSoup(html.content, 'lxml', from_encoding='utf8').find("div", {"class": "company-content fontSizeSmall BSHARE_POP"})
            content = res2.get_text()
            poz = content.index('上一篇')
            content = content[:poz]
            try:
                Book.objects.get(url=url)
            except:
                Book.objects.create(title=title, author_id=1, type='share', b_category_id=1, url=url, content=content)

        pages = res.find('div', {'class': 'companies'}).find_all('a')

        for page in pages:
            if page.get_text() == '下一页':
                next_page_url = self.root_url + page['href']
                print(next_page_url)
                yield scrapy.Request(next_page_url, callback=self.parse)
