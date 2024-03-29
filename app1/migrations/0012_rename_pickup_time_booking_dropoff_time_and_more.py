# Generated by Django 5.0.1 on 2024-02-17 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0011_alter_car_regno'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='pickup_time',
            new_name='dropoff_time',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='pickup_date',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='pickup_location',
        ),
        migrations.AddField(
            model_name='booking',
            name='nod',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
