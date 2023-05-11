# Generated by Django 4.1.6 on 2023-05-11 15:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0016_flight_totalavailabeseats_alter_flight_arrivaltime_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='flight',
            old_name='totalAvailabeSeats',
            new_name='totalAvailableSeats',
        ),
        migrations.AlterField(
            model_name='flight',
            name='arrivalTime',
            field=models.TimeField(default=datetime.time(15, 19, 9, 481633)),
        ),
        migrations.AlterField(
            model_name='flight',
            name='departureTime',
            field=models.TimeField(default=datetime.time(15, 19, 9, 481633)),
        ),
    ]
