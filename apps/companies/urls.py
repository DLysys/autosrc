from django.conf.urls import url
from . import views
from django.urls import path

app_name = 'companies'

urlpatterns = [
    url(r'', views.index, name="index"),
    # path(r'company/<int:company_id>.html', views.companyDetailView.as_view(), name="company_detail"),
    #
    # path(r'^author/<int:author_id>.html', views.author_detail, name="author_detail"),
    #
    # url(r'^comment$', views.company_comment, name="company_comment"),
    # url(r'^type/(?P<type>.*)$', views.company_type, name="company_type"),
    # url(r'^category/(?P<category_id>[0-9]+)$', views.company_category, name="company_category"),  # 书分类
    # url(r'^add/$', views.company_add, name="company_add"),
    # url(r'^support$', views.company_support, name="company_support"),
    # url(r'^collect$', views.company_collect, name="company_collect"),
    #
    # path(r'edit/<int:company_id>.html', views.company_edit, name="company_edit"),
    # url(r'^search$', views.company_search, name="company_search"),
    # url(r'^about$', views.about, name="about"),
    # url(r'^google7c5c39bd4748d567.html$', views.google_search, name="google_search"),
    # url(r'^baidu_verify_Z85YzIi6cp.html$', views.baidu_search, name="baidu_search"),

]
