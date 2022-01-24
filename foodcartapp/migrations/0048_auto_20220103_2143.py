# Generated by Django 3.2 on 2022-01-03 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_auto_20211213_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('processed', 'обработанный'), ('unprocessed', 'необработанный')], db_index=True, default='unprocessed', max_length=20, verbose_name='статус'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('cash', 'наличностью'), ('creditcard', 'электронно')], db_index=True, default='не указано', max_length=20, verbose_name='способ оплаты'),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details_orders', to='foodcartapp.order', verbose_name='заказ'),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details_products', to='foodcartapp.product', verbose_name='продукт'),
        ),
    ]