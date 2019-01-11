import os, django
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KnackProject.settings")
django.setup()

BOT_NAME = 'crawlend'
SPIDER_MODULES = ['crawlend.spiders']
NEWSPIDER_MODULE = 'crawlend.spiders'

DOWNLOAD_HANDLERS = {'s3': None}
DOWNLOAD_DELAY = 0.5
DOWNLOAD_TIMEOUT = 100
CONCURRENT_REQUESTS_PER_IP = 1
ITEM_PIPELINES = {'crawlend.pipelines.TestbotPipeline': 1, }
