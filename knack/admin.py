from django.contrib import admin
from .models import Knack, Category


class KnackAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'c_time', 'k_category']
    list_filter = ['title', 'author', 'k_category']
    search_fields = ('title', 'author', 'k_category',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'c_time']
    list_filter = ['name', 'c_time']
    search_fields = ('name', 'c_time',)


admin.site.register(Knack, KnackAdmin)
admin.site.register(Category, CategoryAdmin)
