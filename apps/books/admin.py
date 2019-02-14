from django.contrib import admin
from .models import Book, Category, Chapter, Author


class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'c_time', 'category']
    list_filter = ['title', 'author', 'category']
    search_fields = ('title', 'author', 'category',)


class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'c_time']
    list_filter = ['title', 'c_time']
    search_fields = ('title', 'c_time')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'c_time']
    list_filter = ['name', 'c_time']
    search_fields = ('name', 'c_time',)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    search_fields = ('name',)


admin.site.register(Book, BookAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Author, AuthorAdmin)
