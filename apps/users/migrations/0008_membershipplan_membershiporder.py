# Generated migration for MembershipPlan and MembershipOrder
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_user_member_expire_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='套餐名称')),
                ('level', models.CharField(choices=[('silver', '银卡会员'), ('gold', '金卡会员'), ('platinum', '铂金会员')], max_length=20, verbose_name='会员等级')),
                ('duration_days', models.IntegerField(verbose_name='有效天数')),
                ('original_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='原价')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='现价')),
                ('description', models.TextField(blank=True, verbose_name='套餐描述')),
                ('benefits', models.JSONField(blank=True, default=list, verbose_name='权益列表')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否上架')),
                ('sort_order', models.IntegerField(default=0, verbose_name='排序')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '会员套餐',
                'verbose_name_plural': '会员套餐',
                'db_table': 'membership_plans',
                'ordering': ['sort_order', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MembershipOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.CharField(max_length=50, unique=True, verbose_name='订单号')),
                ('plan_name', models.CharField(max_length=100, verbose_name='套餐名称')),
                ('plan_level', models.CharField(max_length=20, verbose_name='会员等级')),
                ('duration_days', models.IntegerField(verbose_name='有效天数')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='支付金额')),
                ('status', models.CharField(choices=[('pending', '待支付'), ('paid', '已支付'), ('cancelled', '已取消')], default='pending', max_length=20, verbose_name='状态')),
                ('paid_at', models.DateTimeField(blank=True, null=True, verbose_name='支付时间')),
                ('expire_at', models.DateTimeField(blank=True, null=True, verbose_name='会员到期时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='users.membershipplan', verbose_name='会员套餐')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership_orders', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '会员订单',
                'verbose_name_plural': '会员订单',
                'db_table': 'membership_orders',
                'ordering': ['-created_at'],
            },
        ),
    ]
