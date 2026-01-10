"""
消息模块 - 数据模型
包括广告、系统消息等
"""
from django.db import models


class Advertisement(models.Model):
    """广告/轮播图"""
    POSITION_CHOICES = [
        ('home_banner', '首页轮播'),
        ('home_popup', '首页弹窗'),
        ('category_banner', '分类页轮播'),
    ]
    
    title = models.CharField('广告标题', max_length=100)
    image = models.ImageField('广告图片', upload_to='ads/')
    link = models.CharField('跳转链接', max_length=500, blank=True, null=True)
    link_type = models.CharField('链接类型', max_length=20, default='none')  # none/product/url
    link_id = models.IntegerField('关联ID', blank=True, null=True)  # 产品ID等
    position = models.CharField('展示位置', max_length=30, choices=POSITION_CHOICES, default='home_banner')
    sort_order = models.IntegerField('排序', default=0)
    start_time = models.DateTimeField('开始时间', blank=True, null=True)
    end_time = models.DateTimeField('结束时间', blank=True, null=True)
    is_active = models.BooleanField('是否启用', default=True)
    click_count = models.IntegerField('点击次数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'advertisements'
        verbose_name = '广告'
        verbose_name_plural = verbose_name
        ordering = ['sort_order']

    def __str__(self):
        return self.title


class Message(models.Model):
    """系统消息"""
    TYPE_CHOICES = [
        ('system', '系统通知'),
        ('promotion', '促销活动'),
        ('order', '订单通知'),
        ('new_product', '新品上市'),
        ('expiry_warning', '临期提醒'),
    ]
    
    title = models.CharField('消息标题', max_length=100)
    content = models.TextField('消息内容')
    message_type = models.CharField('消息类型', max_length=20, choices=TYPE_CHOICES, default='system')
    image = models.ImageField('消息图片', upload_to='messages/', blank=True, null=True)
    link = models.CharField('跳转链接', max_length=500, blank=True, null=True)
    is_global = models.BooleanField('全局消息', default=True)  # 是否推送给所有用户
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'messages'
        verbose_name = '系统消息'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class UserMessage(models.Model):
    """用户消息记录"""
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='用户'
    )
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE,
        related_name='recipients',
        verbose_name='消息'
    )
    is_read = models.BooleanField('已读', default=False)
    read_at = models.DateTimeField('阅读时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'user_messages'
        verbose_name = '用户消息'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'message']

    def __str__(self):
        return f'{self.user.username} - {self.message.title}'
