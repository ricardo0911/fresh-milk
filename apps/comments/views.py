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
        if self.action in ['list', 'retrieve']:
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
        serializer.save(user=self.request.user)

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
        queryset = Comment.objects.all()
        is_approved = self.request.query_params.get('is_approved')
        product_id = self.request.query_params.get('product_id')
        
        if is_approved is not None:
            queryset = queryset.filter(is_approved=is_approved == 'true')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset

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
