"""
配送模块 - 视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import DeliveryPerson, DeliveryRecord, DeliveryRoute
from .serializers import (
    DeliveryPersonSerializer, DeliveryPersonListSerializer,
    DeliveryRecordSerializer, DeliveryRouteSerializer
)


class DeliveryPersonViewSet(viewsets.ModelViewSet):
    """配送员视图集"""
    queryset = DeliveryPerson.objects.filter(is_active=True)
    serializer_class = DeliveryPersonSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DeliveryPersonListSerializer
        return DeliveryPersonSerializer
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新配送员状态"""
        person = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(DeliveryPerson.STATUS_CHOICES):
            person.status = new_status
            person.save()
            return Response({'message': '状态更新成功'})
        return Response({'error': '无效的状态'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """配送员统计"""
        person = self.get_object()
        today = timezone.now().date()
        
        today_records = person.records.filter(assigned_at__date=today)
        completed = today_records.filter(status='delivered').count()
        
        return Response({
            'total_deliveries': person.total_deliveries,
            'rating': float(person.rating),
            'today_total': today_records.count(),
            'today_completed': completed,
        })


class DeliveryRecordViewSet(viewsets.ModelViewSet):
    """配送记录视图集"""
    queryset = DeliveryRecord.objects.all()
    serializer_class = DeliveryRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = DeliveryRecord.objects.all()
        
        # 筛选
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        delivery_person = self.request.query_params.get('delivery_person')
        if delivery_person:
            queryset = queryset.filter(delivery_person_id=delivery_person)
        
        return queryset.select_related('order', 'delivery_person')
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新配送状态"""
        record = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(DeliveryRecord.STATUS_CHOICES):
            return Response({'error': '无效的状态'}, status=status.HTTP_400_BAD_REQUEST)
        
        record.status = new_status
        
        if new_status == 'picked':
            record.picked_at = timezone.now()
        elif new_status == 'delivered':
            record.delivered_at = timezone.now()
            # 更新订单状态
            record.order.status = 'delivered'
            record.order.delivered_at = timezone.now()
            record.order.save()
            # 更新配送员统计
            if record.delivery_person:
                record.delivery_person.total_deliveries += 1
                record.delivery_person.save()
        
        record.save()
        return Response({'message': '状态更新成功'})


class DeliveryRouteViewSet(viewsets.ModelViewSet):
    """配送路线视图集"""
    queryset = DeliveryRoute.objects.all()
    serializer_class = DeliveryRouteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = DeliveryRoute.objects.all()
        
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(date=date)
        
        delivery_person = self.request.query_params.get('delivery_person')
        if delivery_person:
            queryset = queryset.filter(delivery_person_id=delivery_person)
        
        return queryset.select_related('delivery_person').prefetch_related('records')
