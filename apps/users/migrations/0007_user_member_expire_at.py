# Generated migration for member_expire_at field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_add_subscription_to_pointsrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='member_expire_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='会员到期时间'),
        ),
    ]
