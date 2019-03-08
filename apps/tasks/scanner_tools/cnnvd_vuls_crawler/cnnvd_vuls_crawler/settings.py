# -*- coding: utf-8 -*-

# Scrapy settings for cnnvd_vuls_crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import datetime

BOT_NAME = 'cnnvd_vuls_crawler'

SPIDER_MODULES = ['cnnvd_vuls_crawler.spiders']
NEWSPIDER_MODULE = 'cnnvd_vuls_crawler.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'cnnvd_vuls_crawler (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'cnnvd_vuls_crawler.middlewares.CnnvdVulsCrawlerSpiderMiddleware': 100,
}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
#    'cnnvd_vuls_crawler.pipelines.CnnvdVulsCrawlerPipeline': 300,
     'cnnvd_vuls_crawler.pipelines.MysqlPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


HTTPERROR_ALLOWED_CODES = [521, 400]
# add splash server address：
SPLASH_URL = 'http://localhost:8050'
# set a class for delete duplication
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
# start scrapy-splash cache system
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# log relation settig
# start log setting
LOG_ENABLED = True

# set utf-8 for log
LOG_ENCODING = 'utf-8'

# store log to scrapy_xxxx_xx_xx.log
to_day = datetime.datetime.now()
log_file_path = "log/scrapy_{}_{}_{}.log".format(to_day.year, to_day.month, to_day.day)
LOG_FILE = log_file_path

# log start level is DEBUG
LOG_LEVEL = 'DEBUG'

# don't display log in command line
LOG_STDOUT = False

# MySQL setting
MYSQL_HOST = '10.30.60.94'
MYSQL_DATABASE = 'chuntao_merak'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Bitsec1@'
MYSQL_PORT = 3306

