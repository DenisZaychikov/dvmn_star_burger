# Generated by Django 3.2 on 2022-01-03 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0053_auto_20220103_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('processed', 'обработанный'), ('unprocessed_order', 'необработанный')], db_index=True, default='unprocessed_order', max_length=20, verbose_name='статус'),
        ),
    ]
