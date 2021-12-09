# Generated by Django 2.2.6 on 2021-12-09 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_auto_20211209_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('cash', 'наличностью'), ('creditcard', 'электронно')], default='creditcard', max_length=20, verbose_name='способ оплаты'),
        ),
    ]
