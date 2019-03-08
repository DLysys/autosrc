from django.conf.urls import url
from . import views

app_name = 'tasks'
urlpatterns = [
    url(r'^list/(?P<page>[0-9]+)$', views.task_list, name='task_list'),
    url(r'^search$', views.task_search, name="task_search"),

    url(r'^task_add_edit$', views.task_add_edit, name='task_add_edit'),
    url(r'^change_scan_type/$', views.change_scan_type, name='change_scan_type'),
    url(r'^task_del/$', views.task_del, name='task_del'),
    url(r'^task_action/$', views.task_action, name='task_action'),
    url(r'^task_detail/$', views.task_detail, name='task_detail'),
    url(r'^task_report/$', views.task_report, name='task_report'),

    url(r'^user/list/$', views.tasktablelist, name='tasklist'),
    # url(r'^user/nessus/scan/$', Scantasks.ScanAll, name='scantask'),
    # url(r'^user/details/<str:task_id>/$', views.taskdetails, name='taskdetails'),
    url(r'^user/scan/action/<str:task_id>/<str:action>/$', views.task_action, name='taskaction'),
    url(r'^user/tasks/action/<str:task_id>/<str:action>/$', views.taskrequestaction, name='taskrequestaction'),
    url(r'^manage/sync/$', views.TaskSync, name='tasksync'),
    url(r'^request/$', views.TaskRequestView, name='taskrequestview'),
    url(r'^request/list/$', views.taskrequesttablelist, name='taskrequestlist'),
]
