# Generated by Django 5.0.4 on 2024-07-29 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesdoctorbot', '0004_warehouseproduct_shelf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storeproduct',
            name='quantity',
            field=models.IntegerField(default=0, verbose_name='Quantity'),
        ),
    ]
