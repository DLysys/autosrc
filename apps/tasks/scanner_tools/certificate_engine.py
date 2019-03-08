import requests
import ssl
import os
import time, datetime
import traceback
import os
import socket
from celery import shared_task
from apps.business.models import Applysys

socket.setdefaulttimeout(1)

danger = '\'"|><`$&*();#\\/:!{}'


# 判断端口是否开放
def is_ssl_alive(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(443)))
        s.shutdown(2)
        return True
    except:
        print(ip + ' closed ')
        return False


def security_check(text):
    for char in danger:
        if char in text:
            return False
    return text


# 获取证书有效期剩余时间
# return 剩余天数
def get_expire_date(domain):
    if not security_check(domain):
        print('alert!alert!someone fucked you by ' + domain)
        return 999
    ret = os.popen(
        'echo | openssl s_client -servername ' + domain + ' -connect ' + domain + ':443 2>/dev/null | openssl x509 -noout -enddate').read()
    ret_s = ret.strip()
    if ret_s.startswith('notAfter='):
        time_original = ret_s.replace('notAfter=', '')
        time_format = datetime.datetime.strptime(time_original, '%b  %d %H:%M:%S %Y %Z')
        print(time_original)

        return (time_format - datetime.datetime.now()).days
    else:
        return 999


# 验证域名的证书是否有效
def cert_veri(domain):
    try:
        requests.get('https://' + domain, timeout=3)
        # print(response.status_code)
        return True
    except requests.exceptions.SSLError as e:
        # print traceback.print_exc()
        # print e.args[0][0]
        if 'certificate verify failed' in e.args[0][0]:
            return False
        if 'doesn\'t match either of' in e.args[0][0]:
            return False
        if 'bad handshake' in e.args[0][0]:
            return True
        return False
    except:
        print(traceback.print_exc())
        return True


@shared_task
def handle(apps):
    issue_domains = []
    expiring_domains = []
    for app in apps:
        domain = app.url
        domain = domain.strip()
        if is_ssl_alive(domain):
            res = cert_veri(domain)
            if not res:
                issue_domains.append(domain)
            else:
                expire_date = int(get_expire_date(domain))
                if expire_date < 30:
                    expiring_domains.append(domain)

    print(issue_domains)
    print(expiring_domains)


def certificate_engine(request, task, action):
    apps = Applysys.objects.all()
    handle.delay(apps)

