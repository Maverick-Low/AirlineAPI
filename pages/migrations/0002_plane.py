# Generated by Django 4.1.6 on 2023-05-08 13:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plane',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('noOfEconomy', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('noOfBusiness', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('noOfFirstClass', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
    ]
