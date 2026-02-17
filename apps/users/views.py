"""
用户模块 - 视图
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash
from django.core.cache import cache
from django.db import transaction
from django.conf import settings
import random
import time
import requests
from .models import User, UserAddress, UserLog, PointsRecord, MembershipPlan, MembershipOrder
from .serializers import (
    UserSerializer, UserRegisterSerializer, UserLoginSerializer,
    ChangePasswordSerializer, UserAddressSerializer, UserLogSerializer,
    PointsRecordSerializer, MembershipPlanSerializer, MembershipOrderSerializer,
    MembershipOrderCreateSerializer
)


def get_wx_session(code):
    """调用微信 code2session 接口获取 openid 和 session_key"""
    wx_config = getattr(settings, 'WECHAT_MINI_PROGRAM', {})
    app_id = wx_config.get('APP_ID', '')
    app_secret = wx_config.get('APP_SECRET', '')

    if not app_id or not app_secret or app_id == 'your_app_id':
        # 开发环境模拟
        return {
            'openid': f'mock_openid_{code[:8] if code else int(time.time())}',
            'session_key': f'mock_session_key_{int(time.time())}',
            'mock': True
        }

    url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': app_id,
        'secret': app_secret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if 'errcode' in data and data['errcode'] != 0:
            return {'error': data.get('errmsg', '微信登录失败')}
        return data
    except Exception as e:
        return {'error': str(e)}


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def wx_login(request):
    """微信登录 - 使用 openid 作为唯一标识"""
    code = request.data.get('code')
    nickname = request.data.get('nickname', '微信用户')
    avatar = request.data.get('avatar', '')

    # 获取 openid
    if code:
        wx_data = get_wx_session(code)
        if 'error' in wx_data:
            return Response({'message': wx_data['error']}, status=status.HTTP_400_BAD_REQUEST)
        openid = wx_data.get('openid')
        session_key = wx_data.get('session_key')
        unionid = wx_data.get('unionid')
    else:
        # 开发环境：没有 code 时生成模拟 openid
        openid = f'dev_openid_{int(time.time())}'
        session_key = f'dev_session_{int(time.time())}'
        unionid = None

    # 通过 openid 查找用户
    try:
        user = User.objects.get(openid=openid)
        # 更新用户信息
        if nickname and nickname != '微信用户':
            user.nickname = nickname
        if avatar:
            user.avatar = avatar
        if session_key:
            user.session_key = session_key
        user.save()
        created = False
    except User.DoesNotExist:
        # 创建新用户
        username = f'wx_{openid[:16]}_{int(time.time())}'
        user = User.objects.create(
            username=username,
            openid=openid,
            unionid=unionid,
            session_key=session_key,
            nickname=nickname or '微信用户',
            avatar=avatar or '',
            is_active=True,
        )
        created = True

    # 生成 JWT token
    refresh = RefreshToken.for_user(user)

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user, context={'request': request}).data,
        'is_new_user': created
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_reset_code(request):
    """发送重置密码验证码"""
    phone = request.data.get('phone')

    if not phone:
        return Response({'message': '请输入手机号'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查用户是否存在
    if not User.objects.filter(phone=phone).exists():
        return Response({'message': '该手机号未注册'}, status=status.HTTP_400_BAD_REQUEST)

    # 生成6位验证码
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    # 存储验证码到缓存 (5分钟有效)
    cache_key = f'reset_code_{phone}'
    cache.set(cache_key, code, 300)

    # TODO: 实际项目中需要调用短信服务发送验证码
    # 开发环境直接返回验证码
    return Response({
        'message': '验证码已发送',
        'code': code  # 开发环境返回，生产环境删除此行
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_reset_code(request):
    """验证重置密码验证码"""
    phone = request.data.get('phone')
    code = request.data.get('code')

    if not phone or not code:
        return Response({'message': '参数不完整'}, status=status.HTTP_400_BAD_REQUEST)

    # 从缓存获取验证码
    cache_key = f'reset_code_{phone}'
    stored_code = cache.get(cache_key)

    # 开发环境: 如果没有缓存的验证码，接受任意6位数字
    if not stored_code:
        if len(code) == 6 and code.isdigit():
            reset_token = f'reset_{phone}_{int(time.time())}'
            cache.set(f'reset_token_{phone}', reset_token, 600)
            return Response({'reset_token': reset_token})
        return Response({'message': '验证码已过期'}, status=status.HTTP_400_BAD_REQUEST)

    if code != stored_code:
        return Response({'message': '验证码错误'}, status=status.HTTP_400_BAD_REQUEST)

    # 生成重置token
    reset_token = f'reset_{phone}_{int(time.time())}'
    cache.set(f'reset_token_{phone}', reset_token, 600)  # 10分钟有效

    # 删除验证码
    cache.delete(cache_key)

    return Response({'reset_token': reset_token})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    """重置密码 - 直接通过手机号重置"""
    phone = request.data.get('phone')
    password = request.data.get('password')

    if not phone or not password:
        return Response({'message': '请输入手机号和新密码'}, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 6:
        return Response({'message': '密码至少6位'}, status=status.HTTP_400_BAD_REQUEST)

    # 查找用户
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response({'message': '该手机号未注册'}, status=status.HTTP_400_BAD_REQUEST)

    # 更新密码
    user.set_password(password)
    user.save()

    return Response({'message': '密码重置成功'})


class UserLoginView(TokenObtainPairView):
    """用户登录视图"""
    serializer_class = UserLoginSerializer


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        return UserSerializer

    @action(detail=False, methods=['get', 'put', 'patch', 'post'])
    def me(self, request):
        """获取/更新当前用户信息"""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        # 处理文件上传
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        # 处理头像文件
        if 'avatar' in request.FILES:
            data['avatar'] = request.FILES['avatar']

        serializer = self.get_serializer(user, data=data, partial=True)
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

    @action(detail=False, methods=['get'])
    def points_records(self, request):
        """获取当前用户积分记录"""
        records = PointsRecord.objects.filter(user=request.user)
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = PointsRecordSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PointsRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取用户统计数据（积分、优惠券数量等）"""
        user = request.user
        from apps.coupons.models import UserCoupon
        coupon_count = UserCoupon.objects.filter(user=user, status='unused').count()
        return Response({
            'points': user.points,
            'coupon_count': coupon_count,
        })


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

    @action(detail=True, methods=['post'])
    def adjust_points(self, request, pk=None):
        """管理员调整用户积分"""
        user = self.get_object()
        points = request.data.get('points', 0)
        remark = request.data.get('remark', '管理员调整')

        try:
            points = int(points)
        except (ValueError, TypeError):
            return Response({'message': '积分必须是整数'}, status=status.HTTP_400_BAD_REQUEST)

        if points == 0:
            return Response({'message': '积分变动不能为0'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user.points += points
            if user.points < 0:
                user.points = 0
            user.save()

            PointsRecord.objects.create(
                user=user,
                type='earn' if points > 0 else 'spend',
                source='admin',
                points=points,
                balance=user.points,
                remark=remark
            )

        return Response({
            'message': '积分调整成功',
            'points': user.points
        })

    @action(detail=True, methods=['get'])
    def points_records(self, request, pk=None):
        """获取用户积分记录"""
        user = self.get_object()
        records = PointsRecord.objects.filter(user=user)
        serializer = PointsRecordSerializer(records, many=True)
        return Response(serializer.data)


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


class MembershipPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """会员套餐视图集（只读）"""
    queryset = MembershipPlan.objects.filter(is_active=True)
    serializer_class = MembershipPlanSerializer
    permission_classes = [permissions.AllowAny]  # 允许未登录用户查看套餐


class MembershipOrderViewSet(viewsets.ModelViewSet):
    """会员订单视图集"""
    serializer_class = MembershipOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MembershipOrder.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """创建会员订单"""
        serializer = MembershipOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan_id = serializer.validated_data['plan_id']
        try:
            plan = MembershipPlan.objects.get(pk=plan_id, is_active=True)
        except MembershipPlan.DoesNotExist:
            return Response({'error': '套餐不存在或已下架'}, status=status.HTTP_404_NOT_FOUND)

        # 创建会员订单
        order = MembershipOrder.objects.create(
            user=request.user,
            plan=plan,
            plan_name=plan.name,
            plan_level=plan.level,
            duration_days=plan.duration_days,
            amount=plan.price
        )

        return Response(MembershipOrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """模拟支付会员订单"""
        order = self.get_object()
        if order.status != 'pending':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)

        from django.utils import timezone
        from datetime import timedelta

        # 会员等级优先级（数字越大等级越高）
        level_priority = {
            'regular': 0,
            'silver': 1,
            'gold': 2,
            'platinum': 3,
        }

        with transaction.atomic():
            user = request.user
            now = timezone.now()

            current_level = user.member_level or 'regular'
            new_level = order.plan_level
            current_priority = level_priority.get(current_level, 0)
            new_priority = level_priority.get(new_level, 0)

            # 如果当前会员未过期，在现有基础上叠加时间
            if user.member_expire_at and user.member_expire_at > now:
                new_expire_at = user.member_expire_at + timedelta(days=order.duration_days)
            else:
                new_expire_at = now + timedelta(days=order.duration_days)

            # 更新订单状态
            order.status = 'paid'
            order.paid_at = now
            order.expire_at = new_expire_at
            order.save()

            # 只有新等级更高时才升级，否则只延长时间
            if new_priority > current_priority:
                user.member_level = new_level
                message = f'支付成功，已升级为{order.plan_name}'
            else:
                message = f'支付成功，会员时长已延长{order.duration_days}天'

            user.member_expire_at = new_expire_at
            user.save()

        return Response({
            'message': message,
            'member_level': user.member_level,
            'expire_at': new_expire_at.isoformat()
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消会员订单"""
        order = self.get_object()
        if order.status != 'pending':
            return Response({'error': '只能取消待支付订单'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'cancelled'
        order.save()

        return Response({'message': '订单已取消'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_image(request):
    """
    通用图片上传接口
    POST /api/v1/upload/image/

    支持的图片类型：评论图片、反馈图片等
    """
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    import uuid
    import os

    file = request.FILES.get('file') or request.FILES.get('image')
    if not file:
        return Response({'error': '请选择图片'}, status=status.HTTP_400_BAD_REQUEST)

    # 验证文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return Response({'error': '不支持的图片格式'}, status=status.HTTP_400_BAD_REQUEST)

    # 验证文件大小（最大5MB）
    if file.size > 5 * 1024 * 1024:
        return Response({'error': '图片大小不能超过5MB'}, status=status.HTTP_400_BAD_REQUEST)

    # 生成文件名
    ext = os.path.splitext(file.name)[1] or '.jpg'
    filename = f"{uuid.uuid4().hex}{ext}"

    # 根据类型确定保存路径
    upload_type = request.POST.get('type', 'common')
    if upload_type == 'comment':
        path = f"uploads/comments/{filename}"
    elif upload_type == 'feedback':
        path = f"uploads/feedbacks/{filename}"
    else:
        path = f"uploads/common/{filename}"

    # 保存文件
    saved_path = default_storage.save(path, ContentFile(file.read()))

    # 返回完整URL
    file_url = request.build_absolute_uri(f'/media/{saved_path}')

    return Response({
        'url': file_url,
        'path': saved_path
    })


