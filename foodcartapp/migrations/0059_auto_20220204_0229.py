# Generated by Django 2.2.6 on 2022-02-03 22:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0058_auto_20220204_0229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetails',
            name='fixed_price',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='фиксированная цена'),
        ),
    ]
