"""
反馈模块 - 视图
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Feedback
from .serializers import FeedbackSerializer, FeedbackCreateSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    """反馈视图集(用户端)"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return FeedbackCreateSerializer
        return FeedbackSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AdminFeedbackViewSet(viewsets.ModelViewSet):
    """管理员反馈视图集"""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = Feedback.objects.all()
        status_param = self.request.query_params.get('status')
        feedback_type = self.request.query_params.get('type')
        
        if status_param:
            queryset = queryset.filter(status=status_param)
        if feedback_type:
            queryset = queryset.filter(feedback_type=feedback_type)
        
        return queryset

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """回复反馈"""
        feedback = self.get_object()
        reply_content = request.data.get('reply')
        if not reply_content:
            return Response({'error': '请输入回复内容'}, status=status.HTTP_400_BAD_REQUEST)
        
        feedback.reply = reply_content
        feedback.replied_by = request.user
        feedback.replied_at = timezone.now()
        feedback.status = 'resolved'
        feedback.save()
        
        return Response({'message': '回复成功'})

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新状态"""
        feedback = self.get_object()
        new_status = request.data.get('status')
        if new_status not in ['pending', 'processing', 'resolved', 'closed']:
            return Response({'error': '无效状态'}, status=status.HTTP_400_BAD_REQUEST)
        
        feedback.status = new_status
        feedback.save()
        return Response({'message': '状态更新成功'})
