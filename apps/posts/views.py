"""
社区帖子模块 - 视图
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Topic, Post, PostLike
from .serializers import TopicSerializer, PostSerializer, PostCreateSerializer


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """话题视图集"""
    queryset = Topic.objects.filter(is_active=True)
    serializer_class = TopicSerializer
    permission_classes = [permissions.AllowAny]


class PostViewSet(viewsets.ModelViewSet):
    """帖子视图集"""
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = Post.objects.filter(is_approved=True)
        tab = self.request.query_params.get('tab')
        topic_id = self.request.query_params.get('topic')

        if tab:
            queryset = queryset.filter(tab=tab)
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞帖子"""
        post = self.get_object()
        like, created = PostLike.objects.get_or_create(user=request.user, post=post)
        if created:
            post.likes += 1
            post.save()
            return Response({'message': '点赞成功', 'likes': post.likes})
        return Response({'message': '已点赞', 'likes': post.likes})

    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        """取消点赞"""
        post = self.get_object()
        deleted, _ = PostLike.objects.filter(user=request.user, post=post).delete()
        if deleted:
            post.likes = max(0, post.likes - 1)
            post.save()
            return Response({'message': '取消点赞成功', 'likes': post.likes})
        return Response({'message': '未点赞', 'likes': post.likes})


class AdminTopicViewSet(viewsets.ModelViewSet):
    """管理员话题视图集"""
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminPostViewSet(viewsets.ModelViewSet):
    """管理员帖子视图集"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = Post.objects.all()
        is_approved = self.request.query_params.get('is_approved')
        tab = self.request.query_params.get('tab')

        if is_approved is not None:
            queryset = queryset.filter(is_approved=is_approved.lower() == 'true')
        if tab:
            queryset = queryset.filter(tab=tab)

        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审核通过"""
        post = self.get_object()
        post.is_approved = True
        post.save()
        return Response({'message': '审核通过'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """审核拒绝"""
        post = self.get_object()
        post.is_approved = False
        post.save()
        return Response({'message': '审核拒绝'})
