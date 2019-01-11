from __future__ import unicode_literals
import os
from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = os.path.split(os.path.dirname(__file__))[-1]
    verbose_name = '用户管理'
