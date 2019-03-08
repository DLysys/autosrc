# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CnnvdVulsCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    vul_name = scrapy.Field()
    vul_type = scrapy.Field()
    vul_cve = scrapy.Field()
    vul_level = scrapy.Field()
    vul_time = scrapy.Field()
    reference = scrapy.Field()
    software_version = scrapy.Field()
    vul_assets_num = scrapy.Field()
    vul_description = scrapy.Field()
    solution = scrapy.Field()
    vul_status = scrapy.Field()
    vul_source = scrapy.Field()
    vul_approved = scrapy.Field()
    s_name_id = scrapy.Field()


