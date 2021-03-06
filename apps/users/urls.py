from django.conf.urls import url
from apps.users import views
from django.conf.urls import include


app_name = 'users'

urlpatterns = [
    url(r'^$', views.login_site, name='login_site'),
    url(r'^login$', views.login_site, name='login'),
    url(r'^findpass$', views.find_pass, name='find_pass'),
    url(r'^captcha', include('captcha.urls')),
    url(r'captcha/refresh/$', views.captcha_refresh, name='captcha_refresh'),
    url(r'^register$', views.register, name='register'),
    url(r'^logout$', views.logout_site, name='logout'),
    url(r'^center$', views.user_center, name='user_center'),
    url(r'^set$', views.user_set, name='user_set'),
    url(r'^u/(?P<user_id>[0-9]+)$', views.user_home, name='user_home'),
    url(r'^update/info$', views.update_user_info, name='update_user_info'),
    url(r'^manage/user/disactivate/$', views.user_disactivate, name='userdisactivate'),
    url(r'^manage/userrequest/stop/$', views.user_request_cancle, name='userregiststop'),
    url(r'^img/upload$', views.upload_image, name='img_upload'),
    url(r'^change/password$', views.change_password, name='change_password'),
]
