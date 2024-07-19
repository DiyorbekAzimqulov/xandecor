from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesdoctorbot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouseproduct',
            name='arrivel_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Arrivel date'),
        ),
    ]
