from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^user/', include('users.urls', namespace='users')),
    url(r'^', include('knack.urls', namespace='knack')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
