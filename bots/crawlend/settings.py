import os
import django
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

BOT_NAME = 'crawlend'
SPIDER_MODULES = ['crawlend.spiders']
NEWSPIDER_MODULE = 'crawlend.spiders'

os.environ["DJANGO_SETTINGS_MODULE"] = "ProjectSettings.settings"
django.setup()

ROBOTSTXT_OBEY = False

# DOWNLOAD_HANDLERS = {'s3': None}
# DOWNLOAD_DELAY = 0.5
# DOWNLOAD_TIMEOUT = 100
# CONCURRENT_REQUESTS_PER_IP = 1

ITEM_PIPELINES = {
    'crawlend.pipelines.TestbotPipeline': 300,
}
