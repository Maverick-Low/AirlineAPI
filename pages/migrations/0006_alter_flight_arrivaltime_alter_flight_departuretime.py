# Generated by Django 4.1.6 on 2023-05-10 15:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_remove_flight_eta_remove_flight_etd_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight',
            name='arrivalTime',
            field=models.TimeField(default=datetime.time(15, 33, 58, 252762)),
        ),
        migrations.AlterField(
            model_name='flight',
            name='departureTime',
            field=models.TimeField(default=datetime.time(15, 33, 58, 252762)),
        ),
    ]
