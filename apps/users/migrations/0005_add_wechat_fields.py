# Generated migration for adding WeChat fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_points_pointsrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='openid',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='微信OpenID'),
        ),
        migrations.AddField(
            model_name='user',
            name='unionid',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='微信UnionID'),
        ),
        migrations.AddField(
            model_name='user',
            name='session_key',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='微信SessionKey'),
        ),
    ]
