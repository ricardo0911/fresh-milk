"""
用户模块 - 序列化器
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import User, UserAddress, UserLog


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    member_level_display = serializers.CharField(source='get_member_level_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'address', 
                  'member_level', 'member_level_display', 'is_admin', 
                  'date_joined', 'created_at']
        read_only_fields = ['id', 'is_admin', 'member_level_display', 'date_joined', 'created_at']


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
    """用户登录序列化器"""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 添加自定义字段
        token['username'] = user.username
        token['is_admin'] = user.is_admin
        return token


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
