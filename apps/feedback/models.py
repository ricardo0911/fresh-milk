"""
反馈模块 - 数据模型
"""
from django.db import models


class Feedback(models.Model):
    """用户反馈"""
    TYPE_CHOICES = [
        ('suggestion', '功能建议'),
        ('complaint', '投诉反馈'),
        ('quality', '产品质量'),
        ('delivery', '配送问题'),
        ('other', '其他'),
    ]
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已解决'),
        ('closed', '已关闭'),
    ]
    
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name='用户'
    )
    feedback_type = models.CharField('反馈类型', max_length=20, choices=TYPE_CHOICES, default='suggestion')
    title = models.CharField('反馈标题', max_length=100)
    content = models.TextField('反馈内容')
    images = models.JSONField('图片', default=list, blank=True)
    contact = models.CharField('联系方式', max_length=50, blank=True, null=True)
    status = models.CharField('处理状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    reply = models.TextField('回复内容', blank=True, null=True)
    replied_by = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='replied_feedbacks',
        verbose_name='回复人'
    )
    replied_at = models.DateTimeField('回复时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'feedbacks'
        verbose_name = '用户反馈'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.title}'
