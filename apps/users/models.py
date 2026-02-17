"""
用户模块 - 数据模型
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型"""
    MEMBER_LEVEL_CHOICES = [
        ('regular', '普通会员'),
        ('silver', '银卡会员'),
        ('gold', '金卡会员'),
        ('platinum', '铂金会员'),
    ]

    phone = models.CharField('手机号', max_length=11, blank=True, null=True, unique=True)
    nickname = models.CharField('昵称', max_length=50, blank=True, null=True)
    gender = models.IntegerField('性别', choices=[(0, '未知'), (1, '男'), (2, '女')], default=0)
    birthday = models.DateField('生日', blank=True, null=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    address = models.TextField('收货地址', blank=True, null=True)
    member_level = models.CharField('会员等级', max_length=20, choices=MEMBER_LEVEL_CHOICES, default='regular')
    member_expire_at = models.DateTimeField('会员到期时间', blank=True, null=True)
    points = models.IntegerField('积分', default=0)
    is_admin = models.BooleanField('是否管理员', default=False)
    # 微信相关字段
    openid = models.CharField('微信OpenID', max_length=100, blank=True, null=True, unique=True)
    unionid = models.CharField('微信UnionID', max_length=100, blank=True, null=True)
    session_key = models.CharField('微信SessionKey', max_length=100, blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    def is_member_valid(self):
        """检查会员是否有效（未过期）"""
        from django.utils import timezone
        if self.member_level == 'regular':
            return True  # 普通会员不受时间限制
        if not self.member_expire_at:
            return False  # 付费会员但没有到期时间视为无效
        return self.member_expire_at > timezone.now()

    def get_discount_rate(self):
        """获取会员折扣率（检查会员是否过期）"""
        rates = {
            'regular': 1.0,
            'silver': 0.95,
            'gold': 0.90,
            'platinum': 0.85,
        }
        # 如果会员已过期，返回普通会员折扣
        if not self.is_member_valid():
            return 1.0
        return rates.get(self.member_level, 1.0)


class UserAddress(models.Model):
    """用户收货地址"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    receiver_name = models.CharField('收货人', max_length=50)
    receiver_phone = models.CharField('收货电话', max_length=11)
    province = models.CharField('省份', max_length=50)
    city = models.CharField('城市', max_length=50)
    district = models.CharField('区县', max_length=50)
    detail = models.CharField('详细地址', max_length=200)
    is_default = models.BooleanField('默认地址', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'user_addresses'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.receiver_name} - {self.detail}'


class UserLog(models.Model):
    """用户操作日志"""
    ACTION_CHOICES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('register', '注册'),
        ('order', '下单'),
        ('pay', '支付'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logs', verbose_name='用户')
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    user_agent = models.TextField('User Agent', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'user_logs'
        verbose_name = '用户日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.action}'


class PointsRecord(models.Model):
    """积分记录"""
    TYPE_CHOICES = [
        ('earn', '获得'),
        ('spend', '消费'),
        ('expire', '过期'),
        ('adjust', '调整'),
    ]
    SOURCE_CHOICES = [
        ('order', '订单奖励'),
        ('subscription', '周期购奖励'),
        ('exchange', '兑换优惠券'),
        ('sign', '签到'),
        ('activity', '活动奖励'),
        ('admin', '管理员调整'),
        ('refund', '退款返还'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points_records', verbose_name='用户')
    type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES)
    source = models.CharField('来源', max_length=20, choices=SOURCE_CHOICES)
    points = models.IntegerField('积分变动')
    balance = models.IntegerField('变动后余额')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='points_records', verbose_name='关联订单')
    subscription = models.ForeignKey('subscriptions.Subscription', on_delete=models.SET_NULL, null=True, blank=True, related_name='points_records', verbose_name='关联订阅')
    remark = models.CharField('备注', max_length=200, blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'points_records'
        verbose_name = '积分记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} {self.get_type_display()} {self.points}积分'


class MembershipPlan(models.Model):
    """会员套餐"""
    LEVEL_CHOICES = [
        ('silver', '银卡会员'),
        ('gold', '金卡会员'),
        ('platinum', '铂金会员'),
    ]

    name = models.CharField('套餐名称', max_length=100)
    level = models.CharField('会员等级', max_length=20, choices=LEVEL_CHOICES)
    duration_days = models.IntegerField('有效天数')
    original_price = models.DecimalField('原价', max_digits=10, decimal_places=2)
    price = models.DecimalField('现价', max_digits=10, decimal_places=2)
    description = models.TextField('套餐描述', blank=True)
    benefits = models.JSONField('权益列表', default=list, blank=True)
    is_active = models.BooleanField('是否上架', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'membership_plans'
        verbose_name = '会员套餐'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return f'{self.name} ({self.get_level_display()})'

    def get_discount_display(self):
        """获取折扣显示文本"""
        rates = {'silver': '95折', 'gold': '9折', 'platinum': '85折'}
        return rates.get(self.level, '')


class MembershipOrder(models.Model):
    """会员购买订单"""
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('cancelled', '已取消'),
    ]

    order_no = models.CharField('订单号', max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership_orders', verbose_name='用户')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, related_name='orders', verbose_name='会员套餐')
    plan_name = models.CharField('套餐名称', max_length=100)  # 冗余存储
    plan_level = models.CharField('会员等级', max_length=20)  # 冗余存储
    duration_days = models.IntegerField('有效天数')  # 冗余存储
    amount = models.DecimalField('支付金额', max_digits=10, decimal_places=2)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField('支付时间', blank=True, null=True)
    expire_at = models.DateTimeField('会员到期时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'membership_orders'
        verbose_name = '会员订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_no} - {self.user.username}'

    def save(self, *args, **kwargs):
        if not self.order_no:
            import uuid
            from django.utils import timezone
            self.order_no = f"VIP{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

