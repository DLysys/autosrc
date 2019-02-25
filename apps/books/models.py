from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Book(models.Model):
    """
    书籍
    """
    type_choice = (
        ('share', '书籍'),
        ('help', '求助'),
        ('advice', '建议'),
        ('notice', '公告'),

    )

    title = models.CharField(max_length=100, default='', verbose_name="书籍名称")
    desc = models.CharField(max_length=255, default='', verbose_name="简介")
    category = models.ForeignKey('Category', null=True, blank=True, verbose_name='分类', on_delete=models.CASCADE, related_name='b_category')
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    author = models.ForeignKey('Author', null=True, blank=True, verbose_name='作者', on_delete=models.CASCADE, related_name='book_author')
    support = models.IntegerField(default=0, verbose_name='点赞数')

    # content = models.TextField(verbose_name='内容', default='')
    type = models.CharField(choices=type_choice, max_length=20, default='', verbose_name="类型")
    # url = models.CharField(verbose_name='采集URL', max_length=200, default='')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('books:book_detail', kwargs={'book_id': self.id})

    class Meta:
        verbose_name = '书籍'
        verbose_name_plural = "书籍"


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
        verbose_name_plural = "章节"


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
        verbose_name_plural = "分类"


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
        verbose_name_plural = "作者"


class BookUser(models.Model):
    """ 窍门和用户的关系表 """

    support_choice = (
        (1, '顶'),
        (0, '踩'),
    )

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    support = models.IntegerField(choices=support_choice, default=None, blank=True, null=True)
    comment = models.TextField(verbose_name='评论', default=None, null=True)
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    collect = models.BooleanField(db_column='collect', default=False)

    class Meta:
        verbose_name = '支持对应用户的中间表'
        verbose_name_plural = "评价对应用户的中间表"
        db_table = "book_user_relationship"
        # unique_together = (("book", "user"),)  # 设置联合主键
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
