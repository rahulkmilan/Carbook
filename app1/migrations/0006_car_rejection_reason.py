# Generated by Django 5.0.1 on 2024-02-14 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0005_car_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='rejection_reason',
            field=models.TextField(blank=True),
        ),
    ]
