from scrapy_djangoitem import DjangoItem
from spider_knack.models import TestScrapy


class CrawlendItem(DjangoItem):
    # define the fields for your item here like:
    # name = scrapy.Field()
    django_model = TestScrapy

