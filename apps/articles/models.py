from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ProjectSettings.utils import cache_decorator, cache
import logging

logger = logging.getLogger(__name__)


class Article(models.Model):
    """ 主题 """
    type_choice = (
        ('book', '书籍'),
        ('help', '求助'),
        ('advice', '建议'),
        ('notice', '公告'),
    )
    STATUS_CHOICES = (
        ('d', '草稿'),
        ('p', '发表'),
    )
    COMMENT_STATUS = (
        ('o', '打开'),
        ('c', '关闭'),
    )
    title = models.CharField(max_length=200, default='', verbose_name="主题名称", unique=True)
    desc = models.CharField(max_length=255, default='', verbose_name="简介")
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    status = models.CharField('发布状态', max_length=1, choices=STATUS_CHOICES, default='p')
    comment_status = models.CharField('评论状态', max_length=1, choices=COMMENT_STATUS, default='o')
    views = models.PositiveIntegerField('浏览量', default=0)
    author = models.ForeignKey('Author', null=True, blank=True, verbose_name='发布者', on_delete=models.CASCADE, related_name='article_author')
    support = models.IntegerField(default=0, verbose_name='点赞数')
    content = models.TextField(verbose_name='内容', default='')
    type = models.CharField(choices=type_choice, max_length=20, default='', verbose_name="类型")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('articles:article_type', kwargs={'article_id': self.id})

    class Meta:
        verbose_name = '主题'
        verbose_name_plural = verbose_name
        ordering = ['-c_time']
        get_latest_by = 'id'

    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)
        return reverse('admin:%s_%s_change' % info, args=(self.pk,))

    @cache_decorator(expiration=60 * 100)
    def next_article(self):
        # 下一篇
        return Article.objects.filter(id__gt=self.id, status='p').order_by('id').first()

    @cache_decorator(expiration=60 * 100)
    def prev_article(self):
        # 前一篇
        return Article.objects.filter(id__lt=self.id, status='p').first()


class Book(models.Model):
    """
    书籍
    """
    article = models.OneToOneField('Article', on_delete=models.CASCADE, default=None)  # 非常关键的一对一关联！
    title = models.CharField(max_length=100, default='', verbose_name="书籍名称")
    desc = models.CharField(max_length=255, default='', verbose_name="简介")
    category = models.ForeignKey('Category', null=True, blank=True, verbose_name='分类', on_delete=models.CASCADE, related_name='b_category')
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    author = models.ForeignKey('Author', null=True, blank=True, verbose_name='作者', on_delete=models.CASCADE, related_name='book_author')
    support = models.IntegerField(default=0, verbose_name='点赞数')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '书籍'
        verbose_name_plural = verbose_name


class Chapter(models.Model):
    """
    书籍的章节
    """
    title = models.CharField(max_length=100, default='', verbose_name="章节标题")
    book = models.ForeignKey(Book, null=True, blank=True, verbose_name='归属于哪部书籍', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='内容', default='')

    # desc = models.CharField(max_length=255, default='', verbose_name="简介")
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # author = models.ForeignKey(User, null=True, blank=True, verbose_name='作者', on_delete=models.CASCADE, related_name='author')
    # support = models.IntegerField(default=0, verbose_name='点赞数')

    # type = models.CharField(choices=type_choice, max_length=20, default='', verbose_name="类型")
    # url = models.CharField(verbose_name='采集URL', max_length=200, default='')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('books:book_detail', kwargs={'book_id': self.id})

    class Meta:
        verbose_name = '章节'
        verbose_name_plural = verbose_name


class Category(models.Model):
    """
    书籍分类
    """
    name = models.CharField(max_length=100, default='', verbose_name="分类名称")
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name


class Author(models.Model):
    """
    作者
    """
    name = models.CharField(max_length=100, default='', verbose_name="姓名")
    desc = models.TextField(default='', verbose_name='作者简历')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '作者'
        verbose_name_plural = verbose_name


class ArticleUser(models.Model):
    """ 窍门和用户的关系表 """

    support_choice = (
        (1, '顶'),
        (0, '踩'),
    )

    article = models.ForeignKey(Article, on_delete=models.CASCADE, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    support = models.IntegerField(choices=support_choice, default=None, blank=True, null=True)
    comment = models.TextField(verbose_name='评论', default=None, null=True)
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    collect = models.BooleanField(db_column='collect', default=False)

    class Meta:
        verbose_name = '支持对应用户的中间表'
        verbose_name_plural = verbose_name
        db_table = "article_user_relationship"
        # unique_together = (("article", "user"),)  # 设置联合主键
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


class SiteSettings(models.Model):
    """
    站点设置
    """
    sitename = models.CharField("网站名称", max_length=200, null=False, blank=False, default='')
    site_description = models.TextField("网站描述", max_length=1000, null=False, blank=False, default='')
    site_seo_description = models.TextField("网站SEO描述", max_length=1000, null=False, blank=False, default='')
    site_keywords = models.TextField("网站关键字", max_length=1000, null=False, blank=False, default='')
    article_sub_length = models.IntegerField("文章摘要长度", default=300)
    sidebar_article_count = models.IntegerField("侧边栏文章数目", default=10)
    sidebar_comment_count = models.IntegerField("侧边栏评论数目", default=5)
    show_google_adsense = models.BooleanField('是否显示谷歌广告', default=False)
    google_adsense_codes = models.TextField('广告内容', max_length=2000, null=True, blank=True, default='')
    open_site_comment = models.BooleanField('是否打开网站评论功能', default=True)
    beiancode = models.CharField('备案号', max_length=2000, null=True, blank=True, default='')
    analyticscode = models.TextField("网站统计代码", max_length=1000, null=False, blank=False, default='')
    show_gongan_code = models.BooleanField('是否显示公安备案号', default=False, null=False)
    gongan_beiancode = models.TextField('公安备案号', max_length=2000, null=True, blank=True, default='')
    resource_path = models.CharField("静态文件保存地址", max_length=300, null=False, default='/var/www/resource/')

    class Meta:
        verbose_name = '网站配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sitename

    def clean(self):
        """自定义模型验证，该表只允许有一条记录"""
        if SiteSettings.objects.exclude(id=self.id).count():
            raise ValidationError(_('只能有一个配置'))

    def save(self, *args, **kwargs):
        """存疑，该表的数据并没有初始化成功"""
        logger.info('start save site settings')
        super().save(*args, **kwargs)
        from ProjectSettings.utils import cache
        cache.clear()
