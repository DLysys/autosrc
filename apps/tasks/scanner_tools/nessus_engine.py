# coding:utf-8
from apps.tasks.scanner_tools import nessus
from apps.tasks.tasks import nessus_scan_detail, nessus_asset_scan_detail
from apps.notice.models import Notice
from utils.mails import send_notice_mail
from apps.tasks import models
from django.urls import reverse


def nessus_engine__(request, task, action):
    subtask = task.subtask
    scanner = task.scanner
    scanner_id = scanner.id
    scan_id = subtask.scan_id
    # nessus_scan_detail(scan_id, tasks, scanner_id)
    res = nessus.get_scan_status(scan_id, scanner_id)
    nessus.get_scan_vuln(scan_id, scanner_id, res[1])


def nessus_engine(request, task, action):
    """ 调用nessus工具的api，实现设备的漏洞扫描功能"""
    subtask = task.subtask
    scanner = task.scanner
    scanner_id = scanner.id
    if action == 'running':
        policy = models.Policy.objects.get(id=subtask.policy_id)
        res = nessus.add_nessus_scan(task.task_name, task.task_des, task.target_address, policy.scanner_id, policy.policy_name)
        if models.SubTask.update_error_msg(res, subtask.id):
            scan_id = res[1]
            # 在nesses 的界面中可见
            res = nessus.launch_nessus_scan(scan_id, scanner_id)
            if models.SubTask.update_error_msg(res, subtask.id):
                scan_uuid = res[1]['scan_uuid']
                subtask.subtask_status = action
                subtask.scan_id = scan_id
                subtask.save()
                nessus_asset_scan_detail.delay(scan_id, task, scanner_id)  # 进入监控扫描状态的任务
                # nessus_scan_detail(scan_id, tasks, scanner_id)
    elif action == 'pausing':
        scan_id = subtask.scan_id
        do_res = nessus.pause_nessus_scan(scan_id, scanner_id)
        if do_res:
            task.task_status = action
            task.save()
    elif action == 'stopping':
        scan_id = subtask.scan_id
        res = nessus.stop_nessus_scan(scan_id, scanner_id)
        if models.SubTask.update_error_msg(res, subtask.id):
            subtask.subtask_status = action
            subtask.save()
            data = {
                'notice_title': '任务进度通知',
                'notice_body': '您对' + task.task_name + '的扫描任务已停止，如需查看结果，请重新执行扫描任务',
                'notice_url': reverse("tasks:task_list"),
                'notice_type': 'notice',
                'task_id': task.id,
            }
            user = task.task_user
            Notice.notice_add(user, data)
    elif action == 'resuming':
        scan_id = subtask.scan_id
        do_res = nessus.resume_nessus_scan(scan_id, scanner_id)
        if do_res:
            task.task_status = action
            task.save()


def nessus_asset_engine(request, task, action):
    """ 调用nessus工具进行网络扫描，进而实现资产发现功能"""

    subtask = task.subtask
    scanner = task.scanner
    scanner_id = scanner.id
    if action == 'running':
        policy = models.Policy.objects.get(id=subtask.policy_id)
        res = nessus.add_nessus_scan(task.task_name, task.task_des, task.target_address, policy.scanner_id, policy.policy_name)
        if models.SubTask.update_error_msg(res, subtask.id):
            scan_id = res[1]
            res = nessus.launch_nessus_scan(scan_id, scanner_id)
            if models.SubTask.update_error_msg(res, subtask.id):
                scan_uuid = res[1]['scan_uuid']
                subtask.subtask_status = action
                subtask.scan_id = scan_id
                subtask.save()
                nessus_asset_scan_detail.delay(scan_id, task, scanner_id)
                # nessus_asset_scan_detail(scan_id, tasks, scanner_id)
    elif action == 'pausing':
        scan_id = subtask.scan_id
        do_res = nessus.pause_nessus_scan(scan_id, scanner_id)
        if do_res:
            task.task_status = action
            task.save()
    elif action == 'stopping':
        scan_id = subtask.scan_id
        res = nessus.stop_nessus_scan(scan_id, scanner_id)
        if models.SubTask.update_error_msg(res, subtask.id):
            scan_uuid = res[1]['scan_uuid']
            subtask.subtask_status = action
            subtask.save()
            data = {
                'notice_title': '任务进度通知',
                'notice_body': '您对' + task.task_name + '的扫描任务已停止，如需查看结果，请重新执行扫描任务',
                'notice_url': reverse("tasks:task_list"),
                'notice_type': 'notice',
                'task_id': task.id,
            }
            user = task.task_user
            Notice.notice_add(user, data)
            send_notice_mail(user.email, data)
    elif action == 'resuming':
        scan_id = subtask.scan_id
        do_res = nessus.resume_nessus_scan(scan_id, scanner_id)
        if do_res:
            task.task_status = action
            task.save()
