from django.db import models


class ExpressCompany(models.Model):
    """快递公司配置"""

    CODE_CHOICES = [
        ('SF', '顺丰速运'),
        ('YTO', '圆通速递'),
        ('ZTO', '中通快递'),
        ('YD', '韵达快递'),
        ('JTSD', '极兔速递'),
    ]

    code = models.CharField('快递公司代码', max_length=20, unique=True)
    name = models.CharField('快递公司名称', max_length=50)

    # API配置
    app_id = models.CharField('AppID', max_length=100, blank=True)
    app_key = models.CharField('AppKey', max_length=200, blank=True)
    app_secret = models.CharField('AppSecret', max_length=200, blank=True)
    customer_code = models.CharField('客户编码/月结账号', max_length=100, blank=True)

    # 其他配置
    api_url = models.CharField('API地址', max_length=200, blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    is_default = models.BooleanField('是否默认', default=False)

    # 发件人信息
    sender_name = models.CharField('发件人姓名', max_length=50, blank=True)
    sender_phone = models.CharField('发件人电话', max_length=20, blank=True)
    sender_province = models.CharField('发件省份', max_length=50, blank=True)
    sender_city = models.CharField('发件城市', max_length=50, blank=True)
    sender_district = models.CharField('发件区县', max_length=50, blank=True)
    sender_address = models.CharField('发件详细地址', max_length=200, blank=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '快递公司'
        verbose_name_plural = verbose_name
        db_table = 'express_company'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # 如果设为默认，取消其他默认
        if self.is_default:
            ExpressCompany.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class ExpressOrder(models.Model):
    """快递订单记录"""

    STATUS_CHOICES = [
        ('created', '已下单'),
        ('collected', '已揽收'),
        ('in_transit', '运输中'),
        ('delivering', '派送中'),
        ('signed', '已签收'),
        ('failed', '签收失败'),
        ('cancelled', '已取消'),
    ]

    # 关联订单
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='express_orders',
        verbose_name='关联订单'
    )

    # 快递信息
    express_company = models.ForeignKey(
        ExpressCompany,
        on_delete=models.PROTECT,
        verbose_name='快递公司'
    )
    express_no = models.CharField('快递单号', max_length=50, db_index=True)

    # 状态
    status = models.CharField('物流状态', max_length=20, choices=STATUS_CHOICES, default='created')

    # 收件人信息
    receiver_name = models.CharField('收件人姓名', max_length=50)
    receiver_phone = models.CharField('收件人电话', max_length=20)
    receiver_province = models.CharField('收件省份', max_length=50, blank=True)
    receiver_city = models.CharField('收件城市', max_length=50, blank=True)
    receiver_district = models.CharField('收件区县', max_length=50, blank=True)
    receiver_address = models.CharField('收件详细地址', max_length=200)

    # 费用
    freight = models.DecimalField('运费', max_digits=10, decimal_places=2, default=0)

    # 预约取件
    pickup_time = models.DateTimeField('预约取件时间', null=True, blank=True)
    pickup_code = models.CharField('取件码', max_length=50, blank=True)

    # 时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    collected_at = models.DateTimeField('揽收时间', null=True, blank=True)
    signed_at = models.DateTimeField('签收时间', null=True, blank=True)

    class Meta:
        verbose_name = '快递订单'
        verbose_name_plural = verbose_name
        db_table = 'express_order'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.express_company.name} - {self.express_no}'


class ExpressTrace(models.Model):
    """物流轨迹"""

    express_order = models.ForeignKey(
        ExpressOrder,
        on_delete=models.CASCADE,
        related_name='traces',
        verbose_name='快递订单'
    )

    time = models.DateTimeField('时间')
    status = models.CharField('状态', max_length=50, blank=True)
    description = models.TextField('描述')
    location = models.CharField('位置', max_length=100, blank=True)

    class Meta:
        verbose_name = '物流轨迹'
        verbose_name_plural = verbose_name
        db_table = 'express_trace'
        ordering = ['-time']

    def __str__(self):
        return f'{self.time} - {self.description}'
