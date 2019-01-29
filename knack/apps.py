from __future__ import unicode_literals

from django.apps import AppConfig
import os


from suit.apps import DjangoSuitConfig


class SuitConfig(DjangoSuitConfig):
    # layout = 'horizontal'
    layout = 'vertical'


class KnackConfig(AppConfig):
    name = os.path.split(os.path.dirname(__file__))[-1]
    verbose_name = '窍门'
