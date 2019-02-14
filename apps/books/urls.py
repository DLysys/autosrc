from django.conf.urls import url
from . import views

app_name = 'books'

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^book/(?P<book_id>[0-9]+)/$', views.book_detail, name="book_detail"),
    url(r'^author/(?P<author_id>[0-9]+)/$', views.author_detail, name="author_detail"),

    url(r'^comment/$', views.book_comment, name="book_comment"),
    url(r'^type/(?P<type>.*)/$', views.book_type, name="book_type"),
    url(r'^category/(?P<category_id>[0-9]+)/$', views.boob_category, name="boob_category"),
    url(r'^add/$', views.book_add, name="book_add"),
    url(r'^support/$', views.book_support, name="book_support"),
    url(r'^collect/$', views.book_collect, name="book_collect"),

    url(r'^edit/(?P<book_id>[0-9]+)$', views.book_edit, name="book_edit"),
    url(r'^search/$', views.book_search, name="book_search"),
    url(r'^about$', views.about, name="about"),
    url(r'^google7c5c39bd4748d567.html$', views.google_search, name="google_search"),
    url(r'^baidu_verify_Z85YzIi6cp.html$', views.baidu_search, name="baidu_search"),

]
