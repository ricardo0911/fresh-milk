"""
社区帖子模块 - 数据模型
"""
from django.db import models


class Topic(models.Model):
    """话题"""
    name = models.CharField('话题名称', max_length=100)
    image = models.CharField('话题图片', max_length=500, blank=True, null=True)
    description = models.TextField('话题描述', blank=True, null=True)
    is_active = models.BooleanField('是否启用', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'topics'
        verbose_name = '话题'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name


class Post(models.Model):
    """社区帖子"""
    TAB_CHOICES = [
        ('推荐', '推荐'),
        ('生日礼', '生日礼'),
        ('新鲜日期', '新鲜日期'),
        ('大家都在晒', '大家都在晒'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='用户'
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='话题'
    )
    tab = models.CharField('分类标签', max_length=20, choices=TAB_CHOICES, default='推荐')
    content = models.TextField('帖子内容')
    image = models.CharField('帖子图片', max_length=500, blank=True, null=True)
    images = models.JSONField('图片列表', default=list, blank=True)
    likes = models.IntegerField('点赞数', default=0)
    is_approved = models.BooleanField('已审核', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'posts'
        verbose_name = '帖子'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.content[:20]}'


class PostLike(models.Model):
    """帖子点赞"""
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name='用户'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='liked_by',
        verbose_name='帖子'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'post_likes'
        verbose_name = '帖子点赞'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'post']
