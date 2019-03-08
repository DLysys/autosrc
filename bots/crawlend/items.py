from scrapy_djangoitem import DjangoItem
from apps.companies.models import Book


class CrawlendItem(DjangoItem):
    # define the fields for your item here like:
    # name = scrapy.Field()
    django_model = Book

