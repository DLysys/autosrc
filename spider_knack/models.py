from django.db import models


class TestScrapy(models.Model):
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=255)

    # class Meta:
        # app_label = 'warehouse'
        # db_table = 'test_scrapy'
