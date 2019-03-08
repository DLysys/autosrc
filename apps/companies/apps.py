from django.apps import AppConfig
import os


class BookConfig(AppConfig):
    name = 'apps.' + os.path.split(os.path.dirname(__file__))[-1]
    verbose_name = '书籍'
