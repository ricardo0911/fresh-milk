"""
评论模块 - 视图
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from django.utils import timezone
from .models import Comment, CommentLike
from .serializers import CommentSerializer, CommentCreateSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """评论视图集"""
    queryset = Comment.objects.filter(is_approved=True)

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        queryset = Comment.objects.filter(is_approved=True)
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            # 对于匿名用户，需要在序列化器中处理
            serializer.save()

    @action(detail=False, methods=['get'])
    def my(self, request):
        """获取当前用户的评价列表"""
        if not request.user.is_authenticated:
            return Response({'detail': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)

        queryset = Comment.objects.filter(user=request.user).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CommentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = CommentSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞评论"""
        comment = self.get_object()
        like, created = CommentLike.objects.get_or_create(
            user=request.user, comment=comment
        )
        if created:
            Comment.objects.filter(pk=comment.pk).update(likes=F('likes') + 1)
            return Response({'message': '点赞成功', 'likes': comment.likes + 1})
        else:
            like.delete()
            Comment.objects.filter(pk=comment.pk).update(likes=F('likes') - 1)
            return Response({'message': '取消点赞', 'likes': max(0, comment.likes - 1)})


class AdminCommentViewSet(viewsets.ModelViewSet):
    """管理员评论视图集"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        from django.db.models import Q
        queryset = Comment.objects.select_related('user', 'product', 'order').all()
        
        # 审核状态筛选
        is_approved = self.request.query_params.get('is_approved')
        if is_approved is not None:
            queryset = queryset.filter(is_approved=is_approved == 'true')
        
        # 产品筛选
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # 搜索（产品名或用户名）
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(product__name__icontains=search) | 
                Q(user__username__icontains=search) |
                Q(user__nickname__icontains=search) |
                Q(content__icontains=search)
            )
        
        # 评分筛选
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=int(rating))
        
        rating_min = self.request.query_params.get('rating_min')
        if rating_min:
            queryset = queryset.filter(rating__gte=int(rating_min))
        
        rating_max = self.request.query_params.get('rating_max')
        if rating_max:
            queryset = queryset.filter(rating__lte=int(rating_max))
        
        # 是否有回复
        has_reply = self.request.query_params.get('has_reply')
        if has_reply == 'true':
            queryset = queryset.exclude(reply__isnull=True).exclude(reply='')
        elif has_reply == 'false':
            queryset = queryset.filter(Q(reply__isnull=True) | Q(reply=''))
        
        # 是否有图片
        has_images = self.request.query_params.get('has_images')
        if has_images == 'true':
            queryset = queryset.exclude(images=[]).exclude(images__isnull=True)
        
        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审核通过"""
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        return Response({'message': '审核通过'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """审核拒绝"""
        comment = self.get_object()
        comment.is_approved = False
        comment.save()
        return Response({'message': '审核拒绝'})

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """回复评论"""
        comment = self.get_object()
        reply_content = request.data.get('reply')
        if not reply_content:
            return Response({'error': '请输入回复内容'}, status=status.HTTP_400_BAD_REQUEST)
        
        comment.reply = reply_content
        comment.replied_at = timezone.now()
        comment.save()
        return Response({'message': '回复成功'})
