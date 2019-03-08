# -*- coding: utf-8 -*-
import shlex
import datetime
import subprocess
import time
# import sys
# import os
# from scrapy.cmdline import execute


def execute_command(cmdstring, cwd=None, timeout=None, shell=False):
    """
    run the shell command
    :param cmdstring:
    :param cwd:
    :param timeout:
    :param shell:
    :return:
    """
    if shell:
        cmdstring_list = cmdstring
    else:
        cmdstring_list = shlex.split(cmdstring)

    if timeout:
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

    sub = subprocess.Popen(cmdstring_list, cwd=cwd, stdin=subprocess.PIPE, shell=shell, bufsize=4096)
    while sub.poll() is None:
        time.sleep(0.1)
        if timeout:
            if end_time <= datetime.datetime.now():
                raise Exception("Timeout: %s" % cmdstring)
    return str(sub.returncode)


# def execute_command2():
#     sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#     execute('scrapy crawl cnnvd_github'.split())
#     execute('scrapy crawl cnnvd_nucms'.split())
#     execute('scrapy crawl amazon_products -o items.csv -t csv'.split())


if __name__ == "__main__":
    print(execute_command("cd /var/www/html/cmdb/chuntao_merak/tasks/scanner_tools/cnnvd_vuls_crawler; scrapy crawl -a module_id=4 -a module_name='CloudBees Jenkins' -a module_type='middle_ware' -a latest=True cnnvd_vuls_spider",shell=True))
    #print(execute_command("cd /var/www/html/cmdb/chuntao_merak/tasks/scanner_tools/cnnvd_vuls_crawler; scrapy crawl -a module_id=4 -a module_name='CloudBees Jenkins' -a module_type='middle_ware' -a latest=False cnnvd_vuls_spider",shell=True))
