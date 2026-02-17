"""
订阅模块 - 数据模型
"""
from django.db import models
import uuid


class Subscription(models.Model):
    """周期购订阅"""
    STATUS_CHOICES = [
        ('active', '配送中'),
        ('paused', '已暂停'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    FREQUENCY_CHOICES = [
        ('daily', '每天'),
        ('weekly', '每周一次'),
        ('biweekly', '每两周一次'),
        ('monthly', '每月一次'),
    ]

    subscription_no = models.CharField('订阅编号', max_length=32, unique=True)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='用户'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        related_name='subscriptions',
        verbose_name='产品'
    )
    product_name = models.CharField('产品名称', max_length=100)
    product_image = models.CharField('产品图片', max_length=200, blank=True, null=True)

    # 订阅配置
    frequency = models.CharField('配送频率', max_length=20, choices=FREQUENCY_CHOICES, default='weekly')
    quantity = models.IntegerField('每次数量', default=1)
    total_periods = models.IntegerField('总期数', default=12)
    delivered_count = models.IntegerField('已配送期数', default=0)

    # 价格信息
    period_price = models.DecimalField('每期价格', max_digits=10, decimal_places=2)
    total_price = models.DecimalField('总价', max_digits=10, decimal_places=2)

    # 配送信息
    receiver_name = models.CharField('收货人', max_length=50, blank=True, null=True)
    receiver_phone = models.CharField('收货电话', max_length=11, blank=True, null=True)
    receiver_address = models.TextField('收货地址', blank=True, null=True)

    # 日期
    start_date = models.DateField('开始日期')
    next_delivery_date = models.DateField('下次配送日期', blank=True, null=True)

    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')

    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        verbose_name = '周期购订阅'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.subscription_no

    def save(self, *args, **kwargs):
        if not self.subscription_no:
            self.subscription_no = self.generate_subscription_no()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_subscription_no():
        """生成订阅编号"""
        import time
        return f"SUB{time.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"

    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def frequency_display(self):
        return dict(self.FREQUENCY_CHOICES).get(self.frequency, self.frequency)
