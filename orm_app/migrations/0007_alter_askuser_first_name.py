# Generated by Django 5.0.4 on 2024-05-25 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orm_app', '0006_askuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='askuser',
            name='first_name',
            field=models.CharField(default='Mavjud emas', max_length=100),
        ),
    ]
