# Generated by Django 3.2 on 2022-01-14 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0054_alter_order_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('processed', 'обработанный'), ('unprocessed', 'необработанный')], db_index=True, default='unprocessed', max_length=20, verbose_name='статус'),
        ),
    ]