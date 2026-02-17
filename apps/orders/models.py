"""
订单模块 - 数据模型
"""
from django.db import models
import uuid


class Order(models.Model):
    """订单"""
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('shipped', '已发货'),
        ('delivered', '已送达'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('refunding', '退款中'),
        ('refunded', '已退款'),
    ]
    
    order_no = models.CharField('订单号', max_length=32, unique=True)
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='orders',
        verbose_name='用户'
    )
    total_amount = models.DecimalField('订单总额', max_digits=10, decimal_places=2)
    pay_amount = models.DecimalField('实付金额', max_digits=10, decimal_places=2)
    status = models.CharField('订单状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 收货信息
    receiver_name = models.CharField('收货人', max_length=50)
    receiver_phone = models.CharField('收货电话', max_length=11)
    receiver_address = models.TextField('收货地址')
    
    # 配送信息
    delivery_type = models.CharField('配送方式', max_length=20, default='express')
    delivery_fee = models.DecimalField('配送费', max_digits=10, decimal_places=2, default=0)

    # 快递信息
    express_company = models.CharField('快递公司', max_length=20, blank=True, null=True)  # SF/YTO
    express_no = models.CharField('快递单号', max_length=50, blank=True, null=True)
    express_status = models.CharField('物流状态', max_length=20, blank=True, null=True)
    
    # 周期购信息
    is_subscription = models.BooleanField('周期购', default=False)
    subscription_frequency = models.CharField('配送频率', max_length=50, blank=True, null=True)  # 如: 每周一次
    subscription_periods = models.IntegerField('配送期数', default=1)
    current_period = models.IntegerField('当前期数', default=1)
    
    # 备注
    remark = models.TextField('订单备注', blank=True, null=True)
    
    # 时间
    paid_at = models.DateTimeField('支付时间', blank=True, null=True)
    shipped_at = models.DateTimeField('发货时间', blank=True, null=True)
    delivered_at = models.DateTimeField('送达时间', blank=True, null=True)
    completed_at = models.DateTimeField('完成时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'orders'
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = self.generate_order_no()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_order_no():
        """生成订单号"""
        import time
        return f"FM{time.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"


class OrderItem(models.Model):
    """订单商品"""
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name='订单'
    )
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='order_items',
        verbose_name='产品'
    )
    product_name = models.CharField('产品名称', max_length=100)
    product_image = models.CharField('产品图片', max_length=200, blank=True, null=True)
    price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    quantity = models.IntegerField('数量', default=1)
    total_price = models.DecimalField('小计', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'order_items'
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.order.order_no} - {self.product_name}'

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)


class Cart(models.Model):
    """购物车"""
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='cart_items',
        verbose_name='用户'
    )
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.CASCADE,
        related_name='in_carts',
        verbose_name='产品'
    )
    quantity = models.IntegerField('数量', default=1)
    selected = models.BooleanField('已选中', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'carts'
        verbose_name = '购物车'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'


class RefundRequest(models.Model):
    """退款申请"""
    TYPE_CHOICES = [
        ('refund_only', '仅退款'),
        ('return_refund', '退货退款'),
    ]
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('approved', '已同意'),
        ('rejected', '已拒绝'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    REASON_CHOICES = [
        ('quality', '商品质量问题'),
        ('not_on_time', '未按时送达'),
        ('not_match', '商品与描述不符'),
        ('no_need', '不想要了'),
        ('other', '其他'),
    ]

    refund_no = models.CharField('退款单号', max_length=32, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refund_requests', verbose_name='订单')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='refund_requests', verbose_name='用户')

    type = models.CharField('退款类型', max_length=20, choices=TYPE_CHOICES, default='refund_only')
    reason = models.CharField('退款原因', max_length=50, choices=REASON_CHOICES)
    description = models.TextField('详细说明', blank=True, null=True)
    amount = models.DecimalField('退款金额', max_digits=10, decimal_places=2)
    images = models.TextField('图片凭证', blank=True, null=True)  # JSON数组

    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')

    admin = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_refunds', verbose_name='处理人')
    admin_remark = models.TextField('处理备注', blank=True, null=True)
    reject_reason = models.CharField('拒绝原因', max_length=200, blank=True, null=True)

    return_express_company = models.CharField('退货快递公司', max_length=20, blank=True, null=True)
    return_express_no = models.CharField('退货快递单号', max_length=50, blank=True, null=True)
    return_address = models.CharField('退货地址', max_length=200, blank=True, null=True)

    processed_at = models.DateTimeField('处理时间', blank=True, null=True)
    completed_at = models.DateTimeField('完成时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'refund_requests'
        verbose_name = '退款申请'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.refund_no

    def save(self, *args, **kwargs):
        if not self.refund_no:
            self.refund_no = self.generate_refund_no()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_refund_no():
        """生成退款单号"""
        import time
        return f"RF{time.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"


class Payment(models.Model):
    """支付记录"""
    PAYMENT_METHOD_CHOICES = [
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
        ('sandbox', '沙箱测试'),
    ]
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('success', '支付成功'),
        ('failed', '支付失败'),
        ('refunded', '已退款'),
    ]
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='payments',
        verbose_name='订单'
    )
    payment_no = models.CharField('支付流水号', max_length=64, unique=True)
    trade_no = models.CharField('第三方交易号', max_length=64, blank=True, null=True)
    amount = models.DecimalField('支付金额', max_digits=10, decimal_places=2)
    method = models.CharField('支付方式', max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField('支付状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField('支付时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'payments'
        verbose_name = '支付记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.payment_no
