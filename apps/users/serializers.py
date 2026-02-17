"""
用户模块 - 序列化器
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import User, UserAddress, UserLog, PointsRecord, MembershipPlan, MembershipOrder


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    member_level_display = serializers.CharField(source='get_member_level_display', read_only=True)
    is_member_valid = serializers.SerializerMethodField()

    def get_is_member_valid(self, obj):
        return obj.is_member_valid()

    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'email', 'phone', 'avatar', 'gender', 'birthday', 'address',
                  'member_level', 'member_level_display', 'member_expire_at', 'is_member_valid',
                  'points', 'is_admin', 'is_staff', 'is_active', 'date_joined', 'created_at']
        read_only_fields = ['id', 'is_admin', 'is_staff', 'member_level_display', 'member_expire_at',
                           'is_member_valid', 'points', 'date_joined', 'created_at']

    def to_representation(self, instance):
        """输出时返回头像完整URL"""
        data = super().to_representation(instance)
        if instance.avatar:
            request = self.context.get('request')
            if request:
                data['avatar'] = request.build_absolute_uri(instance.avatar.url)
            else:
                data['avatar'] = instance.avatar.url
        else:
            data['avatar'] = ''
        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '两次密码不一致'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(TokenObtainPairSerializer):
    """用户登录序列化器 - 支持用户名或手机号登录"""
    username = serializers.CharField(required=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 添加自定义字段
        token['username'] = user.username
        token['is_admin'] = user.is_admin
        return token

    def validate(self, attrs):
        # 获取输入的用户名（可能是手机号）
        username_or_phone = attrs.get('username')
        password = attrs.get('password')

        # 尝试通过手机号查找用户
        user = None
        if username_or_phone:
            # 先尝试手机号
            try:
                user = User.objects.get(phone=username_or_phone)
                attrs['username'] = user.username  # 替换为真实用户名
            except User.DoesNotExist:
                # 再尝试用户名
                try:
                    user = User.objects.get(username=username_or_phone)
                except User.DoesNotExist:
                    pass

        if not user:
            raise serializers.ValidationError({'detail': '用户不存在'})

        # 验证密码
        if not user.check_password(password):
            raise serializers.ValidationError({'detail': '密码错误'})

        if not user.is_active:
            raise serializers.ValidationError({'detail': '账号已被禁用'})

        # 调用父类验证生成token
        data = super().validate(attrs)
        # 添加用户信息到响应
        data['user'] = UserSerializer(self.user, context=self.context).data
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])


class UserAddressSerializer(serializers.ModelSerializer):
    """收货地址序列化器"""
    class Meta:
        model = UserAddress
        fields = ['id', 'receiver_name', 'receiver_phone', 'province', 'city', 
                  'district', 'detail', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserLogSerializer(serializers.ModelSerializer):
    """用户日志序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserLog
        fields = ['id', 'user', 'username', 'action', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']


class PointsRecordSerializer(serializers.ModelSerializer):
    """积分记录序列化器"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)

    class Meta:
        model = PointsRecord
        fields = ['id', 'type', 'type_display', 'source', 'source_display',
                  'points', 'balance', 'order', 'remark', 'created_at']
        read_only_fields = ['id', 'created_at']


class MembershipPlanSerializer(serializers.ModelSerializer):
    """会员套餐序列化器"""
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    discount_display = serializers.CharField(source='get_discount_display', read_only=True)

    class Meta:
        model = MembershipPlan
        fields = ['id', 'name', 'level', 'level_display', 'duration_days',
                  'original_price', 'price', 'description', 'benefits',
                  'discount_display', 'is_active', 'sort_order']


class MembershipOrderSerializer(serializers.ModelSerializer):
    """会员订单序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    plan_level_display = serializers.SerializerMethodField()

    class Meta:
        model = MembershipOrder
        fields = ['id', 'order_no', 'plan', 'plan_name', 'plan_level', 'plan_level_display',
                  'duration_days', 'amount', 'status', 'status_display',
                  'paid_at', 'expire_at', 'created_at']
        read_only_fields = ['id', 'order_no', 'plan_name', 'plan_level', 'duration_days',
                           'amount', 'status', 'paid_at', 'expire_at', 'created_at']

    def get_plan_level_display(self, obj):
        level_map = {'silver': '银卡会员', 'gold': '金卡会员', 'platinum': '铂金会员'}
        return level_map.get(obj.plan_level, obj.plan_level)


class MembershipOrderCreateSerializer(serializers.Serializer):
    """创建会员订单序列化器"""
    plan_id = serializers.IntegerField()
