"""
消息模块 - 视图
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from django.db.models import F, Q
from .models import Advertisement, Message, UserMessage
from .serializers import AdvertisementSerializer, MessageSerializer, UserMessageSerializer


class AdvertisementViewSet(viewsets.ReadOnlyModelViewSet):
    """广告视图集(用户端)"""
    queryset = Advertisement.objects.filter(is_active=True)
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Advertisement.objects.filter(is_active=True)
        position = self.request.query_params.get('position')
        if position:
            queryset = queryset.filter(position=position)
        
        now = timezone.now()
        queryset = queryset.filter(
            Q(start_time__isnull=True) | Q(start_time__lte=now),
            Q(end_time__isnull=True) | Q(end_time__gte=now)
        )
        return queryset

    @action(detail=True, methods=['post'])
    def click(self, request, pk=None):
        """记录点击"""
        ad = self.get_object()
        Advertisement.objects.filter(pk=ad.pk).update(click_count=F('click_count') + 1)
        return Response({'message': 'ok'})


class MessageListViewSet(viewsets.ReadOnlyModelViewSet):
    """消息列表视图集(用户端)"""
    queryset = Message.objects.filter(is_active=True, is_global=True)
    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]


class UserMessageViewSet(viewsets.ModelViewSet):
    """用户消息视图集"""
    serializer_class = UserMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserMessage.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        """标记已读"""
        msg = self.get_object()
        if not msg.is_read:
            msg.is_read = True
            msg.read_at = timezone.now()
            msg.save()
        return Response({'message': '已读'})

    @action(detail=False, methods=['post'])
    def read_all(self, request):
        """全部已读"""
        UserMessage.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({'message': '全部已读'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """未读数量"""
        count = UserMessage.objects.filter(user=request.user, is_read=False).count()
        return Response({'count': count})


class AdminAdvertisementViewSet(viewsets.ModelViewSet):
    """管理员广告视图集"""
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """启用/禁用"""
        ad = self.get_object()
        ad.is_active = not ad.is_active
        ad.save()
        return Response({'message': '操作成功', 'is_active': ad.is_active})


class AdminMessageViewSet(viewsets.ModelViewSet):
    """管理员消息视图集"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """启用/禁用"""
        msg = self.get_object()
        msg.is_active = not msg.is_active
        msg.save()
        return Response({'message': '操作成功', 'is_active': msg.is_active})

    @action(detail=True, methods=['post'])
    def push(self, request, pk=None):
        """推送消息给所有用户"""
        from apps.users.models import User
        msg = self.get_object()
        
        users = User.objects.filter(is_active=True)
        for user in users:
            UserMessage.objects.get_or_create(user=user, message=msg)
        
        return Response({'message': f'已推送给 {users.count()} 位用户'})
