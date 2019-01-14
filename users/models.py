# coding:utf-8
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import django.utils.timezone as timezone
from django.contrib.auth.models import User, Group, Permission


REQUEST_STATUS = (
    ('0', '待审批'),
    ('1', '审批通过'),
    ('2', '审批拒绝'),
)


# 用户附加属性
class Profile(models.Model):
    user = models.OneToOneField(User, verbose_name=u'用户名', on_delete=models.CASCADE)
    sex = models.BooleanField('性别', max_length=1, choices=((0, '男'), (1, '女'),), default=0)
    city = models.CharField('城市', max_length=128, null=True, blank=True)
    date_updated = models.DateTimeField('数据更新日期', auto_now=True, null=True, blank=True)
    mobilephone = models.CharField(u'手机号码', max_length=50)
    description = models.TextField(u'用户简介')
    error_count = models.IntegerField(u'错误登陆', default=0)
    lock_time = models.DateTimeField(u'锁定时间', default=timezone.now)
    email = models.EmailField('邮箱', null=True, blank=True)
    avatar = models.FileField(upload_to='avatar', default=None)
    point = models.IntegerField(u'积分', default=0)

    def __str__(self):
        return self.user

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


# class Admin(models.Model):
#     """ 后台管理 """
#
#     class Meta:
#         verbose_name = '后台管理'
#         verbose_name_plural = "后台管理"
#         permissions = (
#             ('list_admin', u'后台管理页'),
#         )


# class Area(models.Model):
#     name = models.CharField('属地信息', max_length=90, unique=True)
#     parent = models.ForeignKey('self', verbose_name='父级属地', related_name='assetarea_area', null=True, blank=True, on_delete=models.CASCADE)
#
#     def __str__(self):
#         # 显示层级菜单
#         title_list = [self.name]
#         p = self.parent
#         while p:
#             title_list.insert(0, p.name)
#             p = p.parent
#         return '-'.join(title_list)
