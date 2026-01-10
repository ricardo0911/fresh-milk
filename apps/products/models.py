"""
产品模块 - 数据模型
"""
from django.db import models


class Category(models.Model):
    """产品分类"""
    name = models.CharField('分类名称', max_length=50)
    icon = models.CharField('分类图标', max_length=100, blank=True, null=True)
    description = models.TextField('分类描述', blank=True, null=True)
    sort_order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name = '产品分类'
        verbose_name_plural = verbose_name
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class Product(models.Model):
    """牛奶产品"""
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products',
        verbose_name='分类'
    )
    name = models.CharField('产品名称', max_length=100)
    subtitle = models.CharField('副标题', max_length=200, blank=True, null=True)
    price = models.DecimalField('销售价格', max_digits=10, decimal_places=2)
    original_price = models.DecimalField('原价', max_digits=10, decimal_places=2, blank=True, null=True)
    specification = models.CharField('规格', max_length=100, blank=True, null=True)  # 如: 250ml*10瓶
    origin = models.CharField('产地', max_length=100, blank=True, null=True)
    shelf_life = models.IntegerField('保质期(天)', default=7)
    description = models.TextField('产品描述', blank=True, null=True)
    detail = models.TextField('详细介绍', blank=True, null=True)
    cover_image = models.ImageField('封面图', upload_to='products/covers/', blank=True, null=True)
    images = models.JSONField('产品图片', default=list, blank=True)  # 多张图片URL列表
    stock = models.IntegerField('库存', default=0)
    sales_count = models.IntegerField('销量', default=0)
    view_count = models.IntegerField('浏览量', default=0)
    is_hot = models.BooleanField('热门推荐', default=False)
    is_new = models.BooleanField('新品上市', default=False)
    is_subscription = models.BooleanField('支持周期购', default=False)
    is_active = models.BooleanField('是否上架', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = '产品'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """产品图片"""
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='product_images',
        verbose_name='产品'
    )
    image = models.ImageField('图片', upload_to='products/images/')
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        verbose_name = '产品图片'
        verbose_name_plural = verbose_name
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.product.name} - 图片{self.sort_order}'


class Favorite(models.Model):
    """用户收藏"""
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='favorites',
        verbose_name='用户'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='favorited_by',
        verbose_name='产品'
    )
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        verbose_name = '收藏'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'
