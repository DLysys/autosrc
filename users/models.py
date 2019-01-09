# coding:utf-8
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import django.utils.timezone as timezone
from django.contrib.auth.models import User, Group, Permission


class Admin(models.Model):
    """ 后台管理 """

    class Meta:
        verbose_name = '后台管理'
        verbose_name_plural = "后台管理"
        permissions = (
            ('list_admin', u'后台管理页'),
        )


class Area(models.Model):
    name = models.CharField('属地信息', max_length=90, unique=True)
    parent = models.ForeignKey('self', verbose_name='父级属地', related_name='assetarea_area', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        # 显示层级菜单
        title_list = [self.name]
        p = self.parent
        while p:
            title_list.insert(0, p.name)
            p = p.parent
        return '-'.join(title_list)


# 设置菜单
class Menu(models.Model):
    title = models.CharField(u'菜单标题', max_length=25, unique=True)
    icon = models.CharField(u'菜单图标', max_length=50)
    parent = models.ForeignKey('self', verbose_name=u'父菜单', related_name='menu_menu', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        # 显示层级菜单
        title_list = [self.title]
        p = self.parent
        while p:
            title_list.insert(0, p.title)
            p = p.parent
        return '-'.join(title_list)


REQUEST_STATUS = (
    ('0', '待审批'),
    ('1', '审批通过'),
    ('2', '审批拒绝'),
)


# 用户附加属性
class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name=u'用户名', on_delete=models.CASCADE)
    company = models.CharField('公司', max_length=125, null=True)
    department = models.CharField('部门', max_length=128, null=True)
    team = models.CharField('班组', max_length=128, null=True)
    account = models.CharField('账户', max_length=128)
    chinese_name = models.CharField('中文名', max_length=128, null=True, blank=True)
    date_updated = models.DateTimeField('数据更新日期', auto_now=True, null=True, blank=True)
    # user_token = models.CharField('用户token', max_length=128, null=True, blank=True)
    user_num = models.CharField(u'员工编号', max_length=50, null=True, blank=True)
    title = models.CharField(u'职位名称', max_length=50)
    telephone = models.CharField(u'座机号码', max_length=50, null=True, blank=True)
    mobilephone = models.CharField(u'手机号码', max_length=50)
    description = models.TextField(u'用户简介')
    error_count = models.IntegerField(u'错误登陆', default=0)
    lock_time = models.DateTimeField(u'锁定时间', default=timezone.now)
    parent_email = models.EmailField('上级邮箱', null=True, blank=True)
    # parent = models.ForeignKey(User, verbose_name='上级汇报', related_name='user_parent', null=True, blank=True, on_delete=models.CASCADE)
    # area = models.ForeignKey(Area, verbose_name='所属区域', related_name='user_area', null=True, on_delete=models.CASCADE, limit_choices_to={'parent__isnull': True})
    # roles = models.ManyToManyField(Permission, verbose_name=u'所属角色', related_name='user_role')

    def __str__(self):
        return self.account

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = "用户信息"
        app_label = 'auth'
        db_table = "users_profile"


# 当我们创建和更新用户实例时，Profile模块也会被自动创建和更新。
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Profile.objects.create(user=instance)
        profile = Profile()
        profile.user = instance
        profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
