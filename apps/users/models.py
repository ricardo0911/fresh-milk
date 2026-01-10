"""
用户模块 - 数据模型
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型"""
    phone = models.CharField('手机号', max_length=11, blank=True, null=True, unique=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    address = models.TextField('收货地址', blank=True, null=True)
    is_admin = models.BooleanField('是否管理员', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.username


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
