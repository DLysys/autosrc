from celery import shared_task
from apps.assets.models import Port, WeakPassword
import subprocess
import re


def get_asset_can_crack_services(asset):
    """从资产开放服务中，筛选出可破解的服务"""
    support_services = ['ssh', 'mysql']
    asset_ports = Port.objects.filter(asset_id=asset.id)
    services = {}
    for asset_port in asset_ports:
        asset_service = asset_port.service_name
        id = asset_port.id
        for support_service in support_services:
            if support_service in asset_service:
                services[id] = support_service
    return services


def hydra_save_result(id, output):
    """存储hydra扫描结果"""
    results_list = re.findall(r'login: (.*)password: (.*)\n', output, re.M|re.I)
    for r in results_list:
        username = r[0].strip(' ')
        password = r[1]
        WeakPassword.objects.create(port_id=id, username=username, password=password)

        return username, password


@shared_task
def hydra_start(assets, task, subtask):
    print('[+] 开始执行hydra弱口令扫描')
    results = {}
    wps = {}
    for asset in assets:
        services = get_asset_can_crack_services(asset)
        if asset.location == 'inside':
            ip = asset.pri_ip
        else:
            ip = asset.pub_ip
        for id, service in services.items():
            print('扫描IP：', ip)
            import os
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            username_path = BASE_DIR + '/' + '../utils/brute/usernames.txt'
            password_path = BASE_DIR + '/' + '../utils/brute/passwords.txt'

            hydra_command = "/usr/bin/hydra -L %s -P %s %s %s -t 4 -w 5" % (username_path, password_path, ip, service)
            # print(hydra_command)
            result = subprocess.Popen(hydra_command, stdout=subprocess.PIPE, shell=True)
            output = result.stdout.read().decode()
            if 'successfully' in output:
                username, password = hydra_save_result(id, output)
                wps[ip] = {"service": service, "username": username, "password": password}

    print('[+] hydra弱口令扫描任务完成')
    num = len(wps)
    if num:
        results["summary"] = "共发现 %s 个弱口令" % str(num)
        results["wps"] = wps
        print(results)
    else:
        results["summary"] = "未发现弱口令"
        results["wps"] = None
        print(results)
    subtask.subtask_status = 'completed'
    subtask.save()
    task.task_status = 'completed'
    task.scan_result = results
    task.save()


@shared_task
def hydra_stop():
    print('[+] 终止hydra弱口令扫描')

