# coding:utf-8
from __future__ import absolute_import
import time
from celery import shared_task
from celery.utils.log import get_task_logger
from apps.notice.models import Notice
from apps.tasks import models
from apps.tasks.models import Task
from apps.tasks.scanner_tools import awvs
from apps.tasks.scanner_tools import nessus
from utils.mails import send_notice_mail
from bianqueProject.settings.base import SCAN_RESULT_PDF_FILE_PATH, SCAN_REPORT_FORMAT, CNNVD_DIR
from django.urls import reverse
import traceback
from apps.tasks.scanner_tools.cnnvd_vuls_crawler import run_cnnvd_crawler
import subprocess
import logging

# logger = get_task_logger(__name__)
logger = logging.getLogger(__name__)    # 在setting.py中配置的logger


@shared_task
def nessus_scan_detail(scan_id, task, scanner_id):
    try:
        subtask = task.subtask
        while True:
            res = nessus.get_scan_status(scan_id, scanner_id)
            if models.SubTask.update_error_msg(res, subtask.id):
                try:
                    res_status = res[1]['info']['status']
                except:
                    time.sleep(5)
                    continue
                if res[1]['info']['status'] == 'canceled' or res[1]['info']['status'] == 'completed' or res[1]['info']['status'] == 'stopping':

                    # 获取漏洞信息并保存
                    nessus.get_scan_vuln(scan_id, scanner_id, res)

                    # 更新子任务的运行进度
                    # subtask.subtask_status = res_status
                    subtask.subtask_status = 'completed'
                    subtask.save()

                    # 更新task 状态
                    # subtask_count = models.SubTask.objects.filter(task_id=tasks.id).exclude(subtask_status__in=['completed', 'exported', 'aborted']).count()
                    subtask_count = models.SubTask.objects.filter(task_id=task.id, subtask_status__in=['pending', 'running', 'exporting']).count()
                    if subtask_count == 0:
                        task.task_status = 'completed'
                        task.save()
                    # filter = [{"filter": "host.hostname", "quality": "match", "value": tasks.target_address},
                    # {"filter": "severity", "quality": "eq", "value": "Low"}]
                    # data = {"format": SCAN_REPORT_FORMAT, "filter": filter}
                    data = {"format": "pdf",
                     "chapters": "vuln_hosts_summary;vuln_by_host; compliance_exec; remediations; vuln_by_plugin; compliance",
                     "filter.0.quality": "eq", "filter.0.filter": "hostname", "filter.0.value": task.target_address,
                     "filter.search_type": "and"}
                    logger.error(data)
                    res = nessus.post_export_request(scan_id, scanner_id, data)

                    if models.SubTask.update_error_msg(res, subtask.id):
                        file_id = res[1]['file']
                        logger.info(file_id)
                        while True:
                            res = nessus.get_export_status(scan_id, file_id, scanner_id)
                            if models.SubTask.update_error_msg(res, subtask.id) and res[1]['status'] == 'ready':
                                # if res[1]['status'] == 'ready':
                                res = nessus.get_export_download(scan_id, file_id, scanner_id)
                                if models.SubTask.update_error_msg(res, subtask.id):
                                    filename = "scan-result-report-{0}-{1}-{2}.{3}".format(SCAN_REPORT_FORMAT, scanner_id, file_id, SCAN_REPORT_FORMAT)
                                    filepath = "{0}/{1}".format(SCAN_RESULT_PDF_FILE_PATH, filename)
                                    destination = open(filepath, 'wb+')
                                    destination.write(res[1])
                                    destination.close()
                                    subtask.report_name = filename
                                    subtask.subtask_status = 'exported'
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
                                    break
                            time.sleep(10)
                        break
            time.sleep(10)
    except Exception as e:
        traceback.print_exc()


@shared_task
def nessus_asset_scan_detail(scan_id, task, scanner_id):
    print('监控扫描任务是否完成')
    try:
        subtask = task.subtask
        while True:
            res = nessus.get_scan_status(scan_id, scanner_id)
            if models.SubTask.update_error_msg(res, subtask.id):
                try:
                    res_status = res[1]['info']['status']
                    print(str(scan_id) + ' ' + res_status)
                except Exception as e:
                    print(e)
                    time.sleep(30)
                    continue
                if res[1]['info']['status'] == 'canceled' or res[1]['info']['status'] == 'completed' or res[1]['info']['status'] == 'stopping':
                    subtask.subtask_status = res_status
                    subtask.save()
                    # 更新task 状态
                    subtask_count = models.SubTask.objects.filter(task_id=task.id, subtask_status__in=['pending', 'running', 'exporting']).count()
                    if subtask_count == 0:
                        task.task_status = 'completed'
                        task.save()

                    # filter = [{"filter": "host.hostname", "quality": "match", "value": "sample.asset.com"}, {"filter": "severity", "quality": "eq", "value": "Critical"}]
                    # data = {"format": SCAN_REPORT_FORMAT, "filter": filter}
                    data = {"format": "pdf",
                            "chapters": "vuln_hosts_summary;vuln_by_host; compliance_exec; remediations; vuln_by_plugin; compliance",
                            "filter.0.quality": "eq", "filter.0.filter": "hostname",
                            "filter.0.value": task.target_address,
                            "filter.search_type": "and"}
                    logger.error(data)
                    print(data)
                    res = nessus.post_export_request(scan_id, scanner_id, data)
                    if models.SubTask.update_error_msg(res, subtask.id):
                        file_id = res[1]['file']
                        print(file_id)
                        while True:
                            res = nessus.get_export_status(scan_id, file_id, scanner_id)
                            if models.SubTask.update_error_msg(res, subtask.id):
                                if res[1]['status'] == 'ready':
                                    res = nessus.get_export_download(scan_id, file_id, scanner_id)
                                    if models.SubTask.update_error_msg(res, subtask.id):
                                        filename = "scan-result-report-{0}-{1}-{2}.{3}".format(SCAN_REPORT_FORMAT, scanner_id, file_id, SCAN_REPORT_FORMAT)
                                        filepath = "{0}/{1}".format(SCAN_RESULT_PDF_FILE_PATH, filename)
                                        destination = open(filepath, 'wb+')
                                        destination.write(res[1])
                                        destination.close()

                                        # 更新subtask信息
                                        subtask.report_name = filename
                                        subtask.subtask_status = 'exported'
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
                                        break
                            time.sleep(10)
                        break
            time.sleep(10)
    except Exception as e:
        traceback.print_exc()


@shared_task
def awvs_scan_detail(scan_id, task, scanner_id):
    try:
        subtask = task.subtask
        while True:
            res = awvs.get_scan_status(scan_id, scanner_id)
            if models.SubTask.update_error_msg(res, subtask.id):
                try:
                    res_status = res[1]['current_session']['status']
                except Exception as e:
                    time.sleep(5)
                    continue
                if res_status in ['completed', 'aborted']:
                    subtask.subtask_status = res_status
                    subtask.save()

                    # 更新task状态
                    subtask_count = models.SubTask.objects.filter(task_id=task.id).exclude(subtask_status__in=['completed', 'exported', 'aborted']).count()
                    # subtask_count = models.SubTask.objects.filter(task_id=tasks.id, subtask_status__in=['pending', 'running', 'exporting']).count()
                    if subtask_count == 0:
                        task.task_status = 'completed'
                        task.save()

                    res = awvs.report_file_request(scan_id, scanner_id)
                    if models.SubTask.update_error_msg(res, subtask.id):
                        time.sleep(10)
                        while True:
                            res = awvs.report_file_dowload(scanner_id, res[1])
                            if models.SubTask.update_error_msg(res, subtask.id):
                                if res[1].status_code == 200:
                                    # scan-result-report-{SCAN_REPORT_FORMAT}-{scanner_id}-{scan_id}-{subtask.target_id}.{SCAN_REPORT_FORMAT}
                                    filename = "scan-result-report-{0}-{1}-{2}-{3}.{4}".format(SCAN_REPORT_FORMAT, scanner_id, scan_id, subtask.target_id, SCAN_REPORT_FORMAT)
                                    filepath = "{0}/{1}".format(SCAN_RESULT_PDF_FILE_PATH, filename)
                                    destination = open(filepath, 'wb+')
                                    destination.write(res[1].content)
                                    destination.close()

                                    # 保存 子任务状态
                                    subtask.report_name = filename
                                    subtask.subtask_status = 'exported'
                                    subtask.save()

                                    # 发送通知和邮件
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
                                    break
                            time.sleep(10)
                        break
            time.sleep(10)
    except Exception as e:
        traceback.print_exc()


@shared_task
def save_awvs_vulns(scan_id, task_id):
    task = Task.objects.filter(task_id=task_id).first()
    while True:
        status = awvs.get_scan_status(scan_id, task.task_scanner.id)
        if status == 'completed':
            awvs.get_scan_result(scan_id, task_id, task.task_scanner.id)
            task.task_status = 'completed'
            task.save()
            # type_task_list = {'移动应用':'type1','web应用':'type2','操作系统':'type3'}
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
            break
        elif status == 'aborted':
            awvs.get_scan_result(scan_id, task_id, task.task_scanner.id)
            task.task_status = 5
            task.save()
            # type_task_list = {'移动应用':'type1','web应用':'type2','操作系统':'type3'}
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
            break
        else:
            time.sleep(60)


@shared_task
def start_get_domains(request, task, action):
    # getdomains.start_get(tasks, action)
    pass


@shared_task
def start_cnnvd_crawler(policy, module_id, module_name, module_type, task):
    """
    start cnnvd crawler
    :param policy:
    :param module_id:
    :param module_name:
    :param module_type:
    :param task:
    :return:
    """
    subtask = task.subtask
    try:
        spider_name = "cnnvd_vuls_spider"
        cmd = "scrapy crawl -a module_id=%d -a module_name='%s' -a module_type='%s' -a latest=%s %s"

        if 'cnnvd_all_vul_crawler' in policy:
            crawl_status = run_cnnvd_crawler.execute_command(
                cmd % (module_id, module_name, module_type, 'False', spider_name),
                shell=True,
                cwd=CNNVD_DIR
            )
        elif 'cnnvd_latest_vul_crawler' in policy:
            crawl_status = run_cnnvd_crawler.execute_command(
                cmd % (module_id, module_name, module_type, 'True', spider_name),
                shell=True,
                cwd=CNNVD_DIR
            )
        else:
            print('[+] Cannot find the tasks policy.')

        if int(crawl_status) == 0:
            while True:
                try:
                    ret = subprocess.call('ps -ef|grep "scrapy crawl"|grep -v "grep.*scrapy crawl"', shell=True)
                    if ret == 0:
                        time.sleep(300)
                        continue
                    elif ret == 1:
                        subtask.subtask_status = 'completed'
                        print('subtask_status: ', subtask.subtask_status)
                        subtask.save()

                        subtask_count = models.SubTask.objects.filter(task_id=task.id, subtask_status__in=['pending', 'running', 'exporting']).count()
                        if subtask_count == 0:
                            task.task_status = 'completed'
                            task.save()

                        break
                except Exception as e:
                    time.sleep(5)
                    continue
        else:
            print('[+] Run spider %s failed.' % spider_name)
    except Exception as e:
        print(str(e))
