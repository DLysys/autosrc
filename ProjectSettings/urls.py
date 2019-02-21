from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap
from apps.books.models import Book


sitemaps = {
    'books': GenericSitemap({'queryset': Book.objects.all(), 'char_field': 'title'}, priority=0.6),
}

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include('apps.books.urls', namespace='books')),
    url(r'^user/', include('apps.users.urls', namespace='users')),
    url(r'^captcha', include('captcha.urls')),

    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
