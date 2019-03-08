# coding:utf-8

import requests
import json
import requests.packages.urllib3
from apps.tasks.models import Scanner
from utils.com_util import return_def_name

# Create your views here.

verify = False


def get_scannerinfo(scanner_id):
    scanner = Scanner.objects.filter(id=scanner_id).first()

    url = scanner.scanner_url
    Access_Key = scanner.scanner_apikey
    Secret_Key = scanner.scanner_apisec
    return url, Access_Key, Secret_Key


def build_url(url, resource):
    return '{0}{1}'.format(url, resource)


def connect(scanner_id, method, resource, data=None):
    '''
    该模块用来定制连接
    '''
    url, Access_Key, Secret_Key = get_scannerinfo(scanner_id)

    headers = {
        'content-type': 'application/json',
        'X-ApiKeys': 'accessKey = ' + Access_Key + ';secretKey =' + Secret_Key,
    }
    try:
        if data != None:
            data = json.dumps(data)
        requests.packages.urllib3.disable_warnings()
        if method == 'POST':
            r = requests.post(build_url(url, resource), data=data, headers=headers, verify=verify)
        elif method == 'PUT':
            r = requests.put(build_url(url, resource), data=data, headers=headers, verify=verify)
        elif method == 'DELETE':
            r = requests.delete(build_url(url, resource), data=data, headers=headers, verify=verify)
        else:
            r = requests.get(build_url(url, resource), params=data, headers=headers, verify=verify)
    except Exception as e:
        return False, e.message

    # Exit if there is an error.
    if r.status_code == 200:
        if 'download' in resource:
            return True, r.content
        else:
            try:
                r.json()
            except Exception as e:
                # print(e.message)
                return True, None
            return True, r.json()
    else:

        return False, r.json()


def get_policy(scanner_id):
    """
    Get scan policy
    Get all of the scan policy but return only the title and the uuid of
    each policy.
    """
    status, data = connect(scanner_id, 'GET', '/policies')
    if status:
        return status, dict((p['name'], p['template_uuid']) for p in data['policies'])
    else:
        return status, data


def add(name, desc, targets, uuid, scanner_id):
    """
    Add a new scan

    Create a new scan using the policy_id, name, description and targets. The
    scan will be created in the default folder for the user. Return the id of
    the newly created scan.
    """
    scan = {
        'uuid': uuid,
        'settings': {
            'name': name,
            'description': desc,
            'text_targets': targets
        }
    }
    return connect(scanner_id, 'POST', '/scans', scan)


def launch(sid, scanner_id):
    """
    Launch a scan
    Launch the scan specified by the sid.
    """
    return connect(scanner_id, 'POST', '/scans/{0}/launch'.format(sid))


def stop(sid, scanner_id):
    """
    Stop a scan
    Stop the scan specified by the sid.
    """
    return connect(scanner_id, 'POST', '/scans/{0}/stop'.format(sid))


def pause(sid, scanner_id):
    """
    Pause a scan
    Pause the scan specified by the sid.
    """
    data = connect(scanner_id, 'POST', '/scans/{0}/pause'.format(sid))
    return data


def resume(sid, scanner_id):
    """
    Resume a scan
    Resume the scan specified by the sid.
    """
    data = connect(scanner_id, 'POST', '/scans/{0}/resume'.format(sid))
    return data


def details(sid, scanner_id):
    """
    Details a scan
    Details the scan specified by the sid.
    """
    return connect(scanner_id, 'GET', '/scans/{0}'.format(sid))


def export_request(sid, scanner_id, data):
    """
    This request requires can view scan permissions
    Details the scan specified by the sid.
    """
    return connect(scanner_id, 'POST', '/scans/{0}/export'.format(sid), data)


def export_status(sid, fid, scanner_id):
    """
    This request requires can view scan export status
    Details the scan specified by the sid.
    """
    return connect(scanner_id, 'GET', '/scans/{0}/export/{1}/status'.format(sid, fid))


def export_download(sid, fid, scanner_id):
    """
    This request requires can view scan export file
    Details the scan specified by the sid.
    """
    return connect(scanner_id, 'GET', '/scans/{0}/export/{1}/download'.format(sid, fid))


def get_plugin_output(sid, host_id, plugin_id, scanner_id):
    return connect(scanner_id, 'GET', '/scans/{0}/hosts/{1}/plugins/{2}'.format(sid, host_id, plugin_id))


def get_host_details(sid, host_id, scanner_id):
    return connect(scanner_id, 'GET', '/scans/{0}/hosts/{1}'.format(sid, host_id))


if __name__ == '__main__':
    pass
    '''
    policy = get_policy()
    pid = policy['Advanced Scan']
    scan = add('test','this is a test','10.10.19.5',pid)
    scan_id=scan['id']
    print(scan_id)
    scan_uuid=launch(scan_id)
    #res=pause(sid)
    #res=resume(sid)
    while True:
        res = details(scan_id)
        if res['info']['status'] == 'completed':
            res = details(scan_id)['vulnerabilities']
            break
        time.sleep(300)
        
    print(res)
    '''
# accessKey=5bde15831e47912a0021edba2261056cd0343ab7a7dbe3a7da53caaf18f90af3
# secretKey=1530195e4e0ce0347caad84385f50bbda1098b4682eef5bac10df8ea45e30529
# curl - H "X-ApiKeys: accessKey={accessKey}; secretKey={secretKey}" https://localhost:8834/scans
# curl - H "X-ApiKeys: accessKey={bde15831e47912a0021edba2261056cd0343ab7a7dbe3a7da53caaf18f90af3; secretKey=e0ce0347caad84385f50bbda1098b4682eef5bac10df8ea45e30529" https://localhost:8834/scans
