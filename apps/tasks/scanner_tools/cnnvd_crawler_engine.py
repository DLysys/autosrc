# coding:utf-8
from apps.tasks import models
from django.conf import settings
from apps.assets.models import Software
import pymysql
from apps.tasks.scanner_tools.cnnvd_vuls_crawler.cnnvd_vuls_crawler import start_cnnvd_crawler


def cnnvd_all_crawler_engine(request, task, action):
    """
    call cnnvd_crawler to gather all vuls
    :param request:
    :param task:
    :param action:
    :return:
    """
    subtask = task.subtask
    if action == 'running':
        try:
            policy = models.Policy.objects.get(id=subtask.policy_id)
            software_modules = Software.objects.all()
            for software_module in software_modules:
                module_id = software_module.id
                module_name = software_module.s_name
                module_type = software_module.s_type
                start_cnnvd_crawler.delay(policy.policy_name, module_id, module_name, module_type, task)
            subtask.subtask_status = action
            subtask.save()
            task.task_status = action
            task.save()
        except:
            subtask.subtask_status = 'cancelled'
            subtask.save()
            task.task_status = 'cancelled'
            task.save()
    else:
        error = 'Don\'t support other operations. please cancel this tasks'
        print(error)


def cnnvd_latest_crawler_engine(request, task, action):
    """
    call cnnvd_crawler to gather latest vuls
    :param request:
    :param task:
    :param action:
    :return:
    """
    subtask = task.subtask
    if action == 'running':
        try:
            policy = models.Policy.objects.get(id=subtask.policy_id)

            software_modules = Software.objects.all()
            for software_module in software_modules:
                module_id = software_module.id
                module_name = software_module.s_name
                module_type = software_module.s_type
                start_cnnvd_crawler.delay(policy.policy_name, module_id, module_name, module_type, task)
            subtask.subtask_status = action
            subtask.save()
            task.task_status = action
            task.save()
        except:
            subtask.subtask_status = 'cancelled'
            subtask.save()
            task.task_status = 'cancelled'
            task.save()
    else:
        error = 'Don\'t support other operations. please cancel this tasks'
        print(error)



