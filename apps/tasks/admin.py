from django.contrib import admin
from . import models

admin.site.register(models.Task)
admin.site.register(models.Scanner)
admin.site.register(models.Files)
