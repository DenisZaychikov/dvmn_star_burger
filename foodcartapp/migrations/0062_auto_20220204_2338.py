# Generated by Django 2.2.6 on 2022-02-04 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0061_auto_20220204_0310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='lat',
            field=models.FloatField(blank=True, null=True, verbose_name='широта'),
        ),
        migrations.AlterField(
            model_name='order',
            name='lon',
            field=models.FloatField(blank=True, null=True, verbose_name='долгота'),
        ),
    ]
