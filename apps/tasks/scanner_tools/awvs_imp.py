import requests, time
import json
import requests.packages.urllib3
from apps.tasks.models import Scanner
from utils.com_util import return_def_name

verify = False
token = ''


def get_scannerinfo(scanner_id):
    # 获取扫描器信息
    scanner = Scanner.objects.filter(id=scanner_id).first()
    url = scanner.scanner_url
    apikey = scanner.scanner_apikey
    return url, apikey


def build_url(url, resource):
    return '{0}{1}'.format(url, resource)


def connect(method, resource, scanner_id, data=None):
    '''
        该模块用来定制连接
    '''
    url, apikey = get_scannerinfo(scanner_id)

    headers = {
        'content-type': 'application/json',
        'X-Auth': apikey,
    }
    data = json.dumps(data)
    requests.packages.urllib3.disable_warnings()
    try:
        if method == 'POST':
            r = requests.post(build_url(url, resource), data=data, headers=headers, verify=verify)
        elif method == 'PUT':
            r = requests.put(build_url(url, resource), data=data, headers=headers, verify=verify)
        elif method == 'DELETE':
            r = requests.delete(build_url(url, resource), data=data, headers=headers, verify=verify)
        elif method == 'PATCH':
            r = requests.patch(build_url(url, resource), data=data, headers=headers, verify=verify)
        else:
            r = requests.get(build_url(url, resource), params=data, headers=headers, verify=verify)
    except Exception as e:
        return False

    # Exit if there is an error. awvs 201 为insert update 状态码， 204位delete

    if r.status_code == 204:
        return True, None
    elif r.status_code in [200, 201]:
        if 'download' in resource:
            return True, r.content
        else:
            return True, r.json()
    else:
        return False, r.json()
    #
    #
    # if r.status_code in [200, 201]:
    #     if 'download' in resource:
    #         return r.content
    #     else:
    #         return r.json()
    # elif r.status_code == 204:
    #     return True
    # else:
    #     return r.json()
    #
    #
    # if r.status_code == 204:
    #     return True
    # elif r.status_code != 201:
    #     e = r.json()
    #     return e
    #
    # if 'download' in resource:
    #     return r.content
    # else:
    #     return r.json()


def connect_all(method, resource, scanner_id, data=None):
    '''
        该模块用来定制连接
    '''
    url, apikey = get_scannerinfo(scanner_id)

    headers = {
        'content-type': 'application/json',
        'X-Auth': apikey,
    }
    data = json.dumps(data)
    requests.packages.urllib3.disable_warnings()
    try:
        if method == 'POST':
            r = requests.post(build_url(url, resource), data=data, headers=headers, verify=verify)
        elif method == 'PUT':
            r = requests.put(build_url(url, resource), data=data, headers=headers, verify=verify)
        elif method == 'DELETE':
            r = requests.delete(build_url(url, resource), data=data, headers=headers, verify=verify)
        elif method == 'PATCH':
            r = requests.patch(build_url(url, resource), data=data, headers=headers, verify=verify)
        else:
            r = requests.get(build_url(url, resource), params=data, headers=headers, verify=verify)
    except Exception as e:
        return False, e.message
    if r.status_code in [200, 201, 404]:
        return True, r
    else:
        return False, r
    return True, r


def add(address, scanner_id, desc):
    scan = {
        'address': address,
        'description': desc,
        'criticality': '10',
    }

    # status, data = connect('POST', '/api/v1/targets', scanner_id, data=scan)
    return connect('POST', '/api/v1/targets', scanner_id, data=scan)


def getscan(scanner_id):
    return connect('GET', '/api/v1/scans', scanner_id)


def getscanid(target_id, scanner_id):
    status, scans = connect('GET', '/api/v1/scans', scanner_id)
    if status:
        scan_id = None
        for scan in scans['scans']:
            if scan['target_id'] == target_id:
                scan_id = scan['scan_id']
                # return scan_id
                break
        return status, scan_id
    else:
        return status, scans


def getstatus(scan_id, scanner_id):
    return connect('GET', '/api/v1/scans/{0}'.format(scan_id), scanner_id)


def getsessionsid(scan_id, scanner_id):
    data = connect('GET', '/api/v1/scans/{0}'.format(scan_id), scanner_id)

    scan_session_id = data['current_session']['scan_session_id']
    return scan_session_id


def delete(scan_id, scanner_id):
    return connect('DELETE', '/api/v1/scans/{0}'.format(scan_id), scanner_id)


def stop(scan_id, scanner_id):
    return connect('POST', '/api/v1/scans/{0}/abort'.format(scan_id), scanner_id)


def start(target_id, scanner_id):
    '''
    11111111-1111-1111-1111-111111111112    High Risk Vulnerabilities          
    11111111-1111-1111-1111-111111111115    Weak Passwords        
    11111111-1111-1111-1111-111111111117    Crawl Only         
    11111111-1111-1111-1111-111111111116    Cross-site Scripting Vulnerabilities       
    11111111-1111-1111-1111-111111111113    SQL Injection Vulnerabilities         
    11111111-1111-1111-1111-111111111118    quick_profile_2 0   {"wvs": {"profile": "continuous_quick"}}            
    11111111-1111-1111-1111-111111111114    quick_profile_1 0   {"wvs": {"profile": "continuous_full"}}         
    11111111-1111-1111-1111-111111111111    Full Scan   1   {"wvs": {"profile": "Default"}}         
    '''
    scan = {
        'target_id': target_id,
        'profile_id': '11111111-1111-1111-1111-111111111111',
        'schedule': {
            'disable': False,
            'start_date': None,
            'time_sensitive': False,
        }
    }
    return connect('POST', '/api/v1/scans', scanner_id, data=scan)


def configure(target_id, cookie, url, scanner_id):
    conf = {
        'custom_cookies': [{'url': url, 'cookie': cookie}]
    }
    res = connect('PATCH', '/api/v1/scans/{0}/configuration'.format(target_id), scanner_id, data=conf)
    if res:
        data = start(target_id)
    return data


def reportrequest(scan_id, scanner_id):
    '''
    11111111-1111-1111-1111-111111111111    Developer
    21111111-1111-1111-1111-111111111111    XML
    11111111-1111-1111-1111-111111111119    OWASP Top 10 2013 
    11111111-1111-1111-1111-111111111112    Quick
    '''
    data = {'template_id': '11111111-1111-1111-1111-111111111111', 'source': {'list_type': 'scans', 'id_list': [scan_id]}}
    status, res = connect_all('POST', '/api/v1/reports', scanner_id, data=data)
    report = res.headers['Location'].replace('/api/v1/reports/', '/reports/download/')
    return status, report


def download(scanner_id, url):
    return connect_all('GET', url+".pdf", scanner_id)


def getstatistics(scan_id, scan_session_id):
    return connect('GET', '/api/v1/scans/{0}/results/{1}/statistics'.format(scan_id, scan_session_id))


def getscanvulns(scan_id, scan_session_id):
    return connect('GET', '/api/v1/scans/{0}/results/{1}/vulnerabilities'.format(scan_id, scan_session_id))


if __name__ == '__main__':
    '''
    target_id = add('10.10.19.7','this is a test')
    res = delete(target_id)
    res_start = start(target_id)
    scan_id = getscanid(target_id)
    status = getstatus(scan_id)
    res_stop = stop(scan_id)
    delete = delete(scan_id)'''
    # res = getscan()
    # res = getreport ('a050dbac-e021-41fb-940f-e11ad279bd35')
    target_id = add('http://10.10.19.7:8009', 'this is a test')
    data = start(target_id)
    scan_id = getscanid(target_id)
    scan_session_id = getsessionsid(scan_id)
    data = getstatistics(scan_id, scan_session_id)
    data_vuln = getscanvulns(scan_id, scan_session_id)
    print(data)
