# Generated by Django 5.0.4 on 2024-07-27 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesdoctorbot', '0003_store_storeproduct'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouseproduct',
            name='shelf',
            field=models.CharField(blank=True, default='A1', max_length=255, null=True, verbose_name='Shelf'),
        ),
    ]