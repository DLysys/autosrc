from apps.tasks.scanner_tools import nessus_imp
import time
# from VulnManage.models import Advance_vulns,Vulnerability_scan
from apps.assets.models import Asset
from apps.assets import asset_handler
from utils.com_util import return_def_name
import os
from apps.assets import models
from django.db.models import Q


def Get_except_vuln(vuln_type):
    except_vulns = []
    except_vuln_list = Advance_vulns.objects.filter(type=vuln_type)
    if except_vuln_list:
        for except_vuln in except_vuln_list:
            except_vulns.append(except_vuln.vuln_name)
    return except_vulns, except_vuln_list


@return_def_name
def add_nessus_scan(name, introduce, target, scanner_id, policy):
    try:
        status, policies = nessus_imp.get_policy(scanner_id)
        if status:
            pid = policies[policy]
            status, data = nessus_imp.add(name, introduce, target, pid, scanner_id)
            if status:
                scan_id = data['scan']['id']
                return status, scan_id
            else:
                return status, data
        else:
            return status, policy
    except Exception as e:
        print(e)
        # return False, str(e)


@return_def_name
def launch_nessus_scan(scan_id, scanner_id):
    return nessus_imp.launch(scan_id, scanner_id)


def pause_nessus_scan(scan_id, scanner_id):
    scan_uuid = nessus_imp.pause(scan_id, scanner_id)
    return scan_uuid


def resume_nessus_scan(scan_id, scanner_id):
    scan_uuid = nessus_imp.resume(scan_id, scanner_id)
    return scan_uuid


@return_def_name
def stop_nessus_scan(scan_id, scanner_id):
    return nessus_imp.stop(scan_id, scanner_id)


@return_def_name
def get_scan_status(scan_id, scanner_id):
    return nessus_imp.details(scan_id, scanner_id)

@return_def_name
def post_export_request(scan_id, scanner_id, data):
    return nessus_imp.export_request(scan_id, scanner_id, data)


@return_def_name
def get_export_status(scan_id, file_id, scanner_id):
    return nessus_imp.export_status(scan_id, file_id, scanner_id)


@return_def_name
def get_export_download(scan_id, file_id, scanner_id):
    return nessus_imp.export_download(scan_id, file_id, scanner_id)


def get_scan_vuln(scan_id, scanner_id, res):
    # def get_scan_vuln(scan_id, tasks, scanner_id):
    # res = nessus_imp.details(scan_id, scanner_id)

    # 根据 内外网ip保存主机信息
    # 保存漏洞信息
    # 保存端口信息
    # 保存漏洞和端口的映射关系信息

    # hosts = res.get('hosts')
    vul_list = res.get('vulnerabilities')
    if vul_list:
        for vul in vul_list:
            for host in res['hosts']:
                host_id = host['host_id']
                hostname = host['hostname']
                # 根据ping判断当前ip是内网还是外网地址，返回值为0则为内网地址
                ping_status = os.system('ping -c 1 -w 1 %s' % hostname)
                if ping_status:
                    asset, status = Asset.objects.get_or_create(pub_ip=hostname)
                else:
                    asset, status = Asset.objects.get_or_create(pri_ip=hostname)
                # 如果是新创建的资产，需要添加资产信息, status true 为新创建
                if status:
                    asset.asset_type = 'server'
                    asset.save()
                if vul:
                    plugin_id = vul.get('plugin_id')
                    severity = vul.get('severity')
                    """
                        风险等级，只选取非 info的漏洞
                        0: info
                        1: low
                        2: medium
                        3: high
                        4: critical
                    """
                    if not severity:
                        continue
                    outputs_status, outputs_details = nessus_imp.get_plugin_output(scan_id, host_id, plugin_id, scanner_id)
                    if not outputs_status:
                        print("============outputs_details======信息获取失败================")
                        continue
                    # 处理漏洞信息
                    # plugindescription = outputs_details['info']['plugindescription']
                    pluginattributes = outputs_details['info']['plugindescription']['pluginattributes']
                    ref_information = pluginattributes.get('ref_information')
                    if not ref_information:
                        continue
                    plugin_name = pluginattributes.get('plugin_name')
                    description = pluginattributes.get('description')
                    synopsis = pluginattributes.get('synopsis')
                    fname = pluginattributes.get('fname')
                    solution = pluginattributes.get('solution')
                    plugin_information = pluginattributes.get('plugin_information')
                    plugin_publication_date = plugin_information.get('plugin_publication_date')
                    plugin_version = plugin_information.get('plugin_version')
                    plugin_type = plugin_information.get('plugin_type')
                    plugin_id = plugin_information.get('plugin_id')
                    plugin_family = plugin_information.get('plugin_family')
                    plugin_modification_date = plugin_information.get('plugin_modification_date')
                    ref = ref_information.get('ref')
                    for re in ref:
                        if re.get('name') == 'cve':
                            cve = re['values']['value']
                            break
                    else:
                        continue
                    # 有cve的标识的漏洞添加到漏洞公有库中，无cve的漏洞不做处理
                    # cve = ['CVE-2018-9958', 'CVE-2018-9958']
                    # 根据Q查询匹配vul库中数据，如果存在则不处理，如果不存在则新建
                    vul_cve_list_or = " | ".join(["Q(vul_cve__contains='{0}')".format(cv) for cv in cve])
                    vuls = models.Vuls.objects.filter(eval(vul_cve_list_or)).first()
                    if not vuls:
                        # 判断漏洞是否存在于库中,如果不存在则新增
                        vuls = models.Vuls.objects.create(
                            vul_name=plugin_name,
                            vul_cve=",".join(cve),
                            vul_level=models.Vuls.vul_level_choice[int(severity)][0],
                            vul_type='other_vul',
                            vul_status='no_poc',
                            solution=solution,
                            vul_description=description,
                            s_name=plugin_name,
                            software_version=plugin_version.lstrip('$Revision:').rstrip('$').strip(),
                            vul_time=plugin_publication_date,
                        )

                    # 处理端口信息
                    outputs = outputs_details.get('outputs')
                    for output in outputs:
                        ports = output['ports']
                        for port in ports.keys():
                            port_num = port.split('/')[0]
                            # 根据端口和相应资产信息，判断资产下的端口信息是否存在
                            pts = models.Port.objects.filter(asset_id=asset.id, port_num=port_num)
                            # 如果端口不存在，则新插入端口号和资产的关系数据，如果端口号存在，则可直接添加端口和漏洞的映射
                            if pts:
                                pt = pts.first()
                            else:
                                pt = models.Port.objects.create(
                                    port_num=port_num,
                                    asset_id=asset.id,
                                    service_name=plugin_name,
                                    service_version=plugin_version,
                                    listen_addr='0.0.0.0'
                                )
                            try:
                                pv = models.PortVuls.objects.get_or_create(port_id=pt.id, vuls_id=vuls.id)
                            except Exception as e:
                                import traceback
                                traceback.print_exc()


def save_scan_asset(res):
    add_succes, add_error = [], []
    for host in res.get("hosts"):
        ip = host['hostname']
        user = models.User.objects.filter(username='default').first()
        data = {"ip": ip, "sn": ip, "asset_manager": user}
        obj = asset_handler.NewAsset(data)
        status = obj.add_to_new_assets_zone_of_auto_scan()
        status and add_succes.append(ip) or add_error.append(ip)
    return add_succes, add_error





