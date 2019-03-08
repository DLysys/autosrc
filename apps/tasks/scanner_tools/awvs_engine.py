# coding:utf-8
from django.shortcuts import render
from apps.tasks.scanner_tools import awvs
from apps.tasks.scanner_tools import awvs_scan_detail
from apps.notice.models import Notice
from utils.mails import send_notice_mail
from apps.tasks import models
from django.urls import reverse


def awvs_engine__(request, task, action):
    subtask = task.subtask
    scanner = task.scanner
    scanner_id = scanner.id
    awvs_scan_detail(subtask.scan_id, task, scanner_id)


def awvs_engine(request, task, action):
    """ 调用awvs api 对web应用扫描"""
    subtask = task.subtask
    scanner = task.scanner
    scanner_id = scanner.id
    if action == 'running':
        res = awvs.add_scan(scanner_id, task.target_address, task.task_des)
        if models.SubTask.update_error_msg(res, subtask.id):
            target_id = res[1]['target_id']
            status, scan_id = awvs.start_scan(scanner_id, target_id)
            if status and scan_id:
                subtask.target_id = target_id
                subtask.scan_id = scan_id
                subtask.subtask_status = action
                subtask.save()
                task.task_status = action
                task.save()
                awvs_scan_detail.delay(scan_id, task, scanner_id)
                # awvs_scan_detail(scan_id, tasks, scanner_id)
    elif action == 'stopping':
        scan_id = subtask.scan_id
        res = awvs.stop_scan(scan_id, scanner_id)
        if models.SubTask.update_error_msg(res, subtask.id):
            subtask.subtask_status = action
            subtask.save()
            data = {
                'notice_title': '任务进度通知',
                'notice_body': '您对' + task.task_name + '的扫描任务已完成，请及时查看结果',
                'notice_url': reverse("tasks:task_list"),
                'notice_type': 'notice',
                'task_id': task.id,
            }
            user = task.task_user
            Notice.notice_add(user, data)
            send_notice_mail(user.email, data)
    else:
        error = '该类任务暂不支持当前操作，请选择取消任务'
        print(error)


'''
def get_domains(request, tasks, action):
    # 应用系统发现扫描
    start_get_domains.delay(request, tasks, action)
    # start_get_domains(request, tasks, action)
'''