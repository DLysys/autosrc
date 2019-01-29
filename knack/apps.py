from __future__ import unicode_literals

from django.apps import AppConfig
import os


from suit.apps import DjangoSuitConfig
# layout这个参数决定你的网页是初始样式是垂直样式还是水平样式，可选参数为‘horizontal’或‘vertical’
class SuitConfig(DjangoSuitConfig):
    layout = 'horizontal'


class KnackConfig(AppConfig):
    name = os.path.split(os.path.dirname(__file__))[-1]
    verbose_name = '窍门'
