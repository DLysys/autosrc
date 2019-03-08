import nmap
from apps.tasks import models
from apps.assets.models import Asset
from django.db.models import Q
from celery import shared_task


def nmap_port(host, port):
    """扫描指定端口"""
    nm = nmap.PortScanner()
    nm.scan(host, port)
    if nm[host].state() == 'up':
        return nm[host]['tcp'][port]


def nmap_host_all(host):
    """全端口扫描"""
    nm = nmap.PortScanner()
    nm.scan(host, '0-65535')
    if nm[host].state() == 'up':
        return nm[host]['tcp']


def nmap_alive_lists(segment):
    nm = nmap.PortScanner()
    nm.scan(hosts=segment, arguments='-n -sn -PE')

    return nm.all_hosts()


def add_nmap_scan(target, policy):
    if 'nmap_host_discovery' in policy:
        res = nmap_alive_lists(target)

        return res


def nmap_engine(request, task, action):
    """ 调用nmap，实现设备的扫描功能"""
    subtask = task.subtask
    scanner = task.scanner
    scanner_id = scanner.id
    nm = nmap.PortScanner()
    nm_a = nmap.PortScannerAsync()

    if action == 'running':
        subtask.subtask_status = action
        subtask.save()
        nmap_call.delay(subtask, task, nm_a)


@shared_task
def nmap_call(subtask, task, nm_a):
    policy = models.Policy.objects.get(id=subtask.policy_id)
    ips = add_nmap_scan(task.target_address, policy.policy_name)
    new_ip_list = []
    for ip in ips:
        if Asset.objects.filter(Q(pri_ip=ip) | Q(pub_ip=ip)).exists():
            print('该资产已入库！')
        else:
            print('新发现资产: %s' % ip)
            Asset.objects.create(pri_ip=ip, status='not_monitored')
            new_ip_list.append(ip)
    while nm_a.still_scanning():
        print('running')
        nm_a.wait(2)

    subtask.subtask_status = 'completed'
    subtask.save()
    new_ips = ';'.join(new_ip_list)
    # tasks.scan_result = '新发现资产：'
    task.task_status = 'completed'
    task.save()
