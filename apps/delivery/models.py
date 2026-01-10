"""
配送模块 - 数据模型
"""
from django.db import models


class DeliveryPerson(models.Model):
    """配送员"""
    STATUS_CHOICES = [
        ('active', '在岗'),
        ('inactive', '休息'),
        ('busy', '配送中'),
    ]
    
    user = models.OneToOneField(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='delivery_profile',
        verbose_name='关联用户'
    )
    employee_no = models.CharField('工号', max_length=20, unique=True)
    name = models.CharField('姓名', max_length=50)
    phone = models.CharField('电话', max_length=11)
    avatar = models.ImageField('头像', upload_to='delivery/avatars/', blank=True, null=True)
    id_card = models.CharField('身份证号', max_length=18, blank=True, null=True)
    vehicle_type = models.CharField('交通工具', max_length=50, default='电动车')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    
    # 配送区域
    delivery_area = models.TextField('配送区域', blank=True, null=True)
    
    # 统计
    total_deliveries = models.IntegerField('总配送量', default=0)
    rating = models.DecimalField('评分', max_digits=3, decimal_places=2, default=5.00)
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'delivery_persons'
        verbose_name = '配送员'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.employee_no} - {self.name}'


class DeliveryRecord(models.Model):
    """配送记录"""
    STATUS_CHOICES = [
        ('pending', '待配送'),
        ('picked', '已取货'),
        ('delivering', '配送中'),
        ('delivered', '已送达'),
        ('failed', '配送失败'),
    ]
    
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.CASCADE, 
        related_name='delivery_records',
        verbose_name='订单'
    )
    delivery_person = models.ForeignKey(
        DeliveryPerson, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='records',
        verbose_name='配送员'
    )
    status = models.CharField('配送状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 配送信息
    receiver_name = models.CharField('收货人', max_length=50)
    receiver_phone = models.CharField('收货电话', max_length=11)
    receiver_address = models.TextField('收货地址')
    
    # 时间
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)
    picked_at = models.DateTimeField('取货时间', blank=True, null=True)
    delivered_at = models.DateTimeField('送达时间', blank=True, null=True)
    
    # 备注
    remark = models.TextField('备注', blank=True, null=True)
    customer_remark = models.TextField('客户备注', blank=True, null=True)

    class Meta:
        db_table = 'delivery_records'
        verbose_name = '配送记录'
        verbose_name_plural = verbose_name
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.order.order_no} - {self.status}'


class DeliveryRoute(models.Model):
    """配送路线"""
    delivery_person = models.ForeignKey(
        DeliveryPerson, 
        on_delete=models.CASCADE, 
        related_name='routes',
        verbose_name='配送员'
    )
    date = models.DateField('配送日期')
    records = models.ManyToManyField(DeliveryRecord, related_name='route', verbose_name='配送记录')
    
    # 统计
    total_orders = models.IntegerField('订单数', default=0)
    completed_orders = models.IntegerField('完成数', default=0)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'delivery_routes'
        verbose_name = '配送路线'
        verbose_name_plural = verbose_name
        unique_together = ['delivery_person', 'date']

    def __str__(self):
        return f'{self.delivery_person.name} - {self.date}'
