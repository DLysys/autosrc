from __future__ import unicode_literals

from django.apps import AppConfig
import os


class KnackConfig(AppConfig):
    name = os.path.split(os.path.dirname(__file__))[-1]
    verbose_name = '窍门'
