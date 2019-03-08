from django.contrib.auth.models import User
from django.db import models


SCANNER_STATUS = (
    ('启用', '启用'),
    ('禁用', '禁用'),
)

IS_ACTIVE_CHOICE = (
    ('1', '启用'),
    ('0', '禁用'),
)

FILE_TYPE = (
    ('网络设备', '网络设备'),
    ('业务系统', '业务系统'),
    ('漏洞列表', '漏洞列表'),
)

TASK_TYPE = (
    ('company_crawler', '企业信息收集'),

    ('nessus_engine', 'Nessus扫描引擎'),
    # ('nessus_asset_engine', 'Nessus资产发现扫描引擎'),
    ('awvs_engine', 'AWVS扫描引擎'),
    ('nmap_engine', 'NMAP扫描引擎'),
    ('get_domains', '应用系统发现引擎'),
    ('cnnvd_all_crawler_engine', 'cnnvd所有爬虫引擎'),
    ('cnnvd_latest_crawler_engine','cnnvd最新爬虫引擎'),
    ('hydra_engine', '弱口令扫描引擎'),
    ('certificate_engine', '证书扫描引擎'),
)

HAS_USER_INFO = (
    (True, '包含'),
    (False, '不包含'),
)


class Files(models.Model):
    name = models.CharField('名称', max_length=50, null=True)
    file_type = models.CharField('类型', max_length=50, choices=FILE_TYPE)
    file = models.FileField('批量文件', upload_to='files/')
    update_data = models.DateField("更新日期", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '文件'
        verbose_name_plural = "文件"


class Scanner(models.Model):
    scanner_name = models.CharField('扫描器名称', max_length=50)
    scanner_type = models.CharField(choices=TASK_TYPE, max_length=50, default='nessus_engine', blank=True)
    scanner_url = models.URLField('扫描器地址', max_length=50, blank=True)
    scanner_status = models.CharField('扫描器状态', max_length=50, default='启用', choices=SCANNER_STATUS, blank=True)
    scanner_apikey = models.CharField('API_KEY', max_length=100, blank=True, null=True)
    scanner_apisec = models.CharField('API_SEC', max_length=100, blank=True, null=True)
    scanner_des = models.TextField('扫描器描述', blank=True)
    scanner_addtime = models.DateField('开始时间', auto_now_add=True)  # 任务开始时间
    scanner_updatetime = models.DateField('结束时间', auto_now=True)  # 任务结束时间

    def __str__(self):
        return self.scanner_name

    class Meta:
        verbose_name = '扫描器'
        verbose_name_plural = "扫描器"


TASK_STATUS = (
    ("completed", "已完成"),
    ("aborted", "已中止"),
    ("imported", "已导入"),
    ("pending", "待处理"),
    ("running", "正在运行"),
    ("resuming", "正在恢复"),
    ("canceling", "取消"),
    ("cancelled", "已取消"),
    ("pausing", "暂停"),
    ("paused", "已暂停"),
    ("stopping", "停止"),
    ("stopped", "已停止"),
    ("exporting", "导出报告中"),
    ("exported", "导出完成"),
)


class Task(models.Model):
    task_num = models.CharField('任务编号', max_length=50, null=True)  # 任务id
    task_name = models.CharField('任务名称', max_length=200)  # 任务名称
    task_type = models.CharField(choices=TASK_TYPE, verbose_name='任务类型', null=True, max_length=100)
    task_target = models.TextField('任务目标', null=True)  # 任务目标
    target_id = models.CharField('扫描对象ID', max_length=100, null=True)
    task_targetinfo = models.CharField('任务属性', max_length=100, null=True)
    task_des = models.TextField('任务描述信息', null=True)  # 目标描述
    task_status = models.CharField('任务状态', max_length=20, default='pending', choices=TASK_STATUS)
    task_plan_time = models.DateTimeField('计划执行时间', null=True, blank=True)  # 计划执行时间
    task_plan_end_time = models.DateTimeField('计划结束时间', null=True)  # 计划执行时间
    task_starttime = models.DateTimeField('开始时间', auto_now_add=True)  # 任务开始时间
    task_endtime = models.DateTimeField('更新时间', auto_now=True)  # 任务结束时间
    target_address = models.CharField('被测目标IP或者URL', max_length=100, null=True, blank=True)
    target_username = models.CharField('被测目标用户名', max_length=20, default='', blank=True)
    target_password = models.CharField('被测目标密码', max_length=20, default='', blank=True)
    scan_result = models.TextField('扫描结果', null=True)

    def __str__(self):
        return self.task_name

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = "任务"
        ordering = ['-task_endtime']
        permissions = (
            ('task_manage_list', u'任务管理列表页'),
        )


class SubTask(models.Model):
    subtask_name = models.CharField('子任务名称', default='', max_length=30)  # 子任务名称
    subtask_status = models.CharField('任务状态', max_length=20, default='pending', choices=TASK_STATUS)  # 任务状态，四个状态，创建，执行中，结束
    scan_id = models.CharField('扫描编号', max_length=50, null=True, blank=True)
    file_id = models.IntegerField(verbose_name='报告编号', default=1)
    target_id = models.CharField('目标编号', max_length=50, default="", blank=True)
    report_name = models.CharField('导出报告文件名称', max_length=500, null=True, blank=True)
    error_msg = models.CharField('执行异常信息', max_length=500, null=True, blank=True)
    task = models.ForeignKey(Task, related_name='subtask_for_task', on_delete=models.CASCADE, verbose_name='子任务')
    scanner = models.ForeignKey(Scanner, related_name='scan_tool', on_delete=models.CASCADE)

    def __str__(self):
        return self.subtask_name

    @staticmethod
    def update_error_msg(res, subtask_id):
        status = res[0]
        if not status:
            subtask = SubTask.objects.get(id=subtask_id)
            error_msg = subtask.error_msg
            if not error_msg:
                error_msg = {}
                error_msg[res[2]] = {'msg': str(res[1]), 'num': 1}
            else:
                try:
                    error_msg = eval(error_msg)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                defname = error_msg.get(res[2])
                if defname:
                    defname_num = defname['num']+1
                    error_msg[res[2]] = {'msg': str(res[1]), 'num': defname_num}
                    if defname_num >= 3:
                        subtask.error_msg = str(error_msg)
                        subtask.save()
                        raise Exception("===>{0}方法已超出查询次数【3】".format(defname))
                else:
                    error_msg[res[2]] = {'msg': str(res[1]), 'num': 1}
            subtask.error_msg = str(error_msg)
            subtask.save()
        return status
