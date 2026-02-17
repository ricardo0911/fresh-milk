# Generated manually to add express fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='express_company',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='快递公司'),
        ),
        migrations.AddField(
            model_name='order',
            name='express_no',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='快递单号'),
        ),
        migrations.AddField(
            model_name='order',
            name='express_status',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='物流状态'),
        ),
    ]
