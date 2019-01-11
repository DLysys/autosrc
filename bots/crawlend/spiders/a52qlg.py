# -*- coding: utf-8 -*-
import scrapy


class A52qlgSpider(scrapy.Spider):
    name = '52qlg'
    allowed_domains = ['52qlg.com']
    start_urls = ['http://52qlg.com/']

    def parse(self, response):
        pass
