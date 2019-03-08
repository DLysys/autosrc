# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import logging


class CnnvdVulsCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipeline():
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.db = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8',
            port=self.port
        )
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        data = dict(item)
        vul_id_value = data['vul_cve']

        # mysql search sentence
        search_sql = 'SELECT * FROM assets_vuls WHERE vul_cve="%s"' % vul_id_value

        # mysql insert sentence
        keys = ', '.join(data.keys())
        values_format = ', '.join(['%s'] * len(data))
        insert_sql = 'INSERT INTO assets_vuls (%s) VALUES (%s)' % (keys, values_format)

        self.cursor.execute(search_sql)
        if self.cursor.fetchall():
            logging.info('[+] %s already exists in the database, so will not insert' % vul_id_value)
        else:
            self.cursor.execute(insert_sql, tuple(data.values()))
            self.db.commit()
            logging.info('[+] insert %s to the database' % vul_id_value)
        return item



