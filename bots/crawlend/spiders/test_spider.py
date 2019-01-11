import scrapy
from bots.crawlend.items import CrawlendItem


class TestSpider(scrapy.Spider):
    name = "test_spider"
    start_urls = [ 'http://quotes.toscrape.com/tag/humor/', ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            item = CrawlendItem()
            item['text'] = quote.css('span.text::text').extract_first()
            item['author'] = quote.xpath('span/small/text()').extract_first()
            yield item

        next_page = response.css('li.next a::attr("href")').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
