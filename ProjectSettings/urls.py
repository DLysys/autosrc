from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include('apps.users.urls', namespace='users')),
    url(r'^companies/', include('apps.companies.urls', namespace='companies')),
    url(r'^tasks/', include('apps.tasks.urls', namespace='tasks')),
    url(r'^captcha', include('captcha.urls')),

    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
