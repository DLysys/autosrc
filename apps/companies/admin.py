from django.contrib import admin
from .models import Book, Category, Chapter, Author, Company
from pagedown.widgets import AdminPagedownWidget
from django import forms


class CompanyForm(forms.ModelForm):
    content = forms.CharField(widget=AdminPagedownWidget())

    class Meta:
        model = Company
        fields = '__all__'


class CompanyAdmin(admin.ModelAdmin):
    form = CompanyForm
    list_display = ['title', 'c_time', 'type']
    list_filter = ['title', 'type']
    search_fields = ('title', 'type',)


class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'c_time']
    list_filter = ['title', 'author']
    search_fields = ('title', 'author')


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


admin.site.register(Company, CompanyAdmin)
admin.site.register(Book, BookAdmin)

admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Author, AuthorAdmin)
