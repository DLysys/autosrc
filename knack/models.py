from django.db import models
from django.contrib.auth.models import User
from users.models import Profile
from django.utils import timezone


class Knack(models.Model):
    """
    窍门
    """
    type_choice = (
        ('share', '分享'),
        ('help', '求助'),
        ('advice', '建议'),
        ('notice', '公告'),

    )

    title = models.CharField(max_length=100, default='', verbose_name="标题")
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    author = models.ForeignKey(User, null=True, blank=True, verbose_name='作者', on_delete=models.CASCADE, related_name='author')
    k_category = models.ForeignKey('Category', null=True, blank=True, verbose_name='分类', on_delete=models.CASCADE, related_name='k_category')
    content = models.TextField(verbose_name='内容', default='')
    type = models.CharField(choices=type_choice, max_length=20, default='', verbose_name="类型")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '窍门'
        verbose_name_plural = "窍门"


class Category(models.Model):
    """
    窍门分类
    """
    port_can_change = (
        ('yes', '是'),
        ('no', '否'),
    )
    choice_status = (
        ('await', '待安全分析'),
        ('approved', '安全'),
        ('reject', '待整改'),
    )

    name = models.CharField(max_length=100, default='', verbose_name="分类名称")
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # s_ip = models.CharField(max_length=100, default='', verbose_name="源IP地址")
    # s_port = models.CharField(max_length=100, default='', verbose_name="源端口")
    # d_device = models.CharField(max_length=100, default='', verbose_name="目的设备")
    # d_port = models.CharField(max_length=100, default='', verbose_name="目标端口")
    # protocol = models.CharField(max_length=100, default='', verbose_name="协议")
    # p_des = models.CharField(max_length=100, default='', verbose_name="端口说明")
    # port_can_change = models.CharField(choices=port_can_change, default='no', max_length=10, verbose_name='监听端口是否可更改')
    # auth_method = models.CharField(max_length=100, default='', verbose_name="认证方式")
    # encryption = models.CharField(max_length=32, verbose_name='加密方式', null=True, blank=True,)
    # version = models.CharField(max_length=32, verbose_name='版本', null=True, blank=True,)
    # scn = models.CharField(max_length=32, verbose_name='特殊场景', null=True, blank=True,)
    # status = models.CharField(choices=choice_status, default='await', max_length=10, verbose_name='审批状态')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = "分类"


class KnackUser(models.Model):
    """ 资产端口&漏洞的 m2m 中间表 """

    support_choice = (
        (1, '顶'),
        (0, '踩'),
    )

    knack = models.ForeignKey(Knack, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    support = models.IntegerField(choices=support_choice, default=None, blank=True, null=True)
    comment = models.TextField(verbose_name='评论', default=None)
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    # fix_action = models.TextField('处理记录【如忽略，请说明原因!】', null=True)
    # fix_status = models.CharField('修复状态', max_length=30, default='wait', choices=VULN_STATUS)
    # update_data = models.DateTimeField('修复时间', auto_now=True)

    class Meta:
        verbose_name = '支持对应用户的中间表'
        verbose_name_plural = "评价对应用户的中间表"
        db_table = "knack_user_relationship"
        # unique_together = (("knack", "user"),)  # 设置联合主键
        # permissions = (
        #     ('port_vuls_list', u'资产对应漏洞信息中间表'),
        # )


# 访问网站的ip地址和次数
class UserIp(models.Model):
    ip = models.CharField(verbose_name='IP地址', max_length=35)
    count = models.IntegerField(verbose_name='访问次数', default=0)  # 该ip访问次数

    class Meta:
        verbose_name = '访问用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.ip


class VisitNumber(models.Model):
    count = models.IntegerField(verbose_name='网站访问总次数', default=0)  # 网站访问总次数

    class Meta:
        verbose_name = '网站访问总次数'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.count)


# 单日访问量统计
class DayNumber(models.Model):
    day = models.DateField(verbose_name='日期', default=timezone.now)
    count = models.IntegerField(verbose_name='网站访问次数', default=0)  # 网站访问总次数

    class Meta:
        verbose_name = '网站日访问量统计'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.day)
