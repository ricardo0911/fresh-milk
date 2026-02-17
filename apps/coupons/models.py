"""
优惠券模块 - 数据模型
"""
from django.db import models
import uuid


class Coupon(models.Model):
    """优惠券"""
    TYPE_CHOICES = [
        ('discount', '折扣券'),
        ('amount', '满减券'),
        ('shipping', '免运费券'),
    ]
    STATUS_CHOICES = [
        ('active', '有效'),
        ('inactive', '已停用'),
        ('expired', '已过期'),
    ]
    
    code = models.CharField('优惠码', max_length=32, unique=True)
    name = models.CharField('券名称', max_length=100)
    type = models.CharField('券类型', max_length=20, choices=TYPE_CHOICES)
    
    # 优惠值
    discount_percent = models.DecimalField('折扣', max_digits=3, decimal_places=1, default=0)  # 折扣券用，如9.5折
    discount_amount = models.DecimalField('优惠金额', max_digits=10, decimal_places=2, default=0)  # 满减券用
    min_amount = models.DecimalField('最低消费', max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField('最大优惠', max_digits=10, decimal_places=2, default=0)
    
    # 使用限制
    total_count = models.IntegerField('发放总量', default=0)  # 0表示不限
    used_count = models.IntegerField('已使用', default=0)
    per_user_limit = models.IntegerField('每人限领', default=1)
    
    # 有效期
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    
    # 适用范围
    applicable_products = models.ManyToManyField(
        'products.Product', 
        blank=True,
        related_name='applicable_coupons',
        verbose_name='适用产品'
    )
    applicable_categories = models.ManyToManyField(
        'products.Category', 
        blank=True,
        related_name='applicable_coupons',
        verbose_name='适用分类'
    )
    is_all_products = models.BooleanField('全场通用', default=True)
    
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField('使用说明', blank=True, null=True)

    # 积分兑换
    points_required = models.IntegerField('所需积分', default=0)  # 0表示不可兑换
    is_exchangeable = models.BooleanField('可积分兑换', default=False)
    exchange_limit = models.IntegerField('兑换限量', default=0)  # 0表示不限
    exchanged_count = models.IntegerField('已兑换数量', default=0)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'coupons'
        verbose_name = '优惠券'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.code})'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_code():
        """生成优惠码"""
        return f"FM{uuid.uuid4().hex[:8].upper()}"


class UserCoupon(models.Model):
    """用户优惠券"""
    STATUS_CHOICES = [
        ('unused', '未使用'),
        ('used', '已使用'),
        ('expired', '已过期'),
    ]
    
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='coupons',
        verbose_name='用户'
    )
    coupon = models.ForeignKey(
        Coupon, 
        on_delete=models.CASCADE, 
        related_name='user_coupons',
        verbose_name='优惠券'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='unused')
    
    received_at = models.DateTimeField('领取时间', auto_now_add=True)
    used_at = models.DateTimeField('使用时间', blank=True, null=True)
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='used_coupons',
        verbose_name='使用订单'
    )

    class Meta:
        db_table = 'user_coupons'
        verbose_name = '用户优惠券'
        verbose_name_plural = verbose_name
        ordering = ['-received_at']

    def __str__(self):
        return f'{self.user.username} - {self.coupon.name}'


class CouponActivity(models.Model):
    """优惠券活动"""
    name = models.CharField('活动名称', max_length=100)
    description = models.TextField('活动描述', blank=True, null=True)
    coupons = models.ManyToManyField(Coupon, related_name='activities', verbose_name='关联优惠券')
    
    banner_image = models.ImageField('活动横幅', upload_to='coupons/banners/', blank=True, null=True)
    
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'coupon_activities'
        verbose_name = '优惠券活动'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
