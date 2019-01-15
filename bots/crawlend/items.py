from scrapy_djangoitem import DjangoItem
from knack.models import Knack


class CrawlendItem(DjangoItem):
    # define the fields for your item here like:
    # name = scrapy.Field()
    django_model = Knack

