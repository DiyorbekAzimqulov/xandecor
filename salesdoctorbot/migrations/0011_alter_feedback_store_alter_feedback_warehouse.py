# Generated by Django 5.0.4 on 2024-08-07 15:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesdoctorbot', '0010_feedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='salesdoctorbot.store'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='salesdoctorbot.warehouse'),
        ),
    ]
