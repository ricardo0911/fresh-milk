"""
用户模块 - 视图
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import update_session_auth_hash
from .models import User, UserAddress, UserLog
from .serializers import (
    UserSerializer, UserRegisterSerializer, UserLoginSerializer,
    ChangePasswordSerializer, UserAddressSerializer, UserLogSerializer
)


class UserLoginView(TokenObtainPairView):
    """用户登录视图"""
    serializer_class = UserLoginSerializer


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        return UserSerializer

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """获取/更新当前用户信息"""
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': '原密码错误'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            return Response({'message': '密码修改成功'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAddressViewSet(viewsets.ModelViewSet):
    """收货地址视图集"""
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 如果设为默认地址，取消其他默认
        if serializer.validated_data.get('is_default'):
            UserAddress.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.validated_data.get('is_default'):
            UserAddress.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
        serializer.save()

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """设为默认地址"""
        address = self.get_object()
        UserAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
        address.is_default = True
        address.save()
        return Response({'message': '设置成功'})


class AdminUserViewSet(viewsets.ModelViewSet):
    """管理员用户管理视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = User.objects.all()
        username = self.request.query_params.get('username')
        phone = self.request.query_params.get('phone')
        if username:
            queryset = queryset.filter(username__icontains=username)
        if phone:
            queryset = queryset.filter(phone__icontains=phone)
        return queryset

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """启用/禁用用户"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'message': '操作成功', 'is_active': user.is_active})


class UserLogViewSet(viewsets.ReadOnlyModelViewSet):
    """用户日志视图集"""
    queryset = UserLog.objects.all()
    serializer_class = UserLogSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = UserLog.objects.all()
        user_id = self.request.query_params.get('user_id')
        action = self.request.query_params.get('action')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action=action)
        return queryset
