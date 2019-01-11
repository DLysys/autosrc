from django.conf.urls import url
from . import views

app_name = 'knack'

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^detail/(?P<knack_id>[0-9]+)/$', views.knack_detail, name="knack_detail"),
    url(r'^comment/$', views.knack_comment, name="knack_comment"),
    url(r'^type/(?P<type>.*)/$', views.knack_type, name="knack_type"),
    url(r'^category/(?P<category_id>[0-9]+)/$', views.knack_category, name="knack_category"),
    url(r'^add/$', views.knack_add, name="knack_add"),
    url(r'^search/$', views.knack_search, name="knack_search"),

]
