"""
评论模块 - 数据模型
"""
from django.db import models


class Comment(models.Model):
    """产品评论"""
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='用户'
    )
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='产品'
    )
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='comments',
        verbose_name='订单'
    )
    rating = models.IntegerField('评分', default=5)  # 1-5星
    content = models.TextField('评论内容')
    images = models.JSONField('评论图片', default=list, blank=True)
    likes = models.IntegerField('点赞数', default=0)
    is_anonymous = models.BooleanField('匿名评论', default=False)
    is_approved = models.BooleanField('已审核', default=True)
    reply = models.TextField('商家回复', blank=True, null=True)
    replied_at = models.DateTimeField('回复时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'comments'
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'


class CommentLike(models.Model):
    """评论点赞"""
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE,
        verbose_name='用户'
    )
    comment = models.ForeignKey(
        Comment, 
        on_delete=models.CASCADE,
        related_name='liked_by',
        verbose_name='评论'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'comment_likes'
        verbose_name = '评论点赞'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'comment']
