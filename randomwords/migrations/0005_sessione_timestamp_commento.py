# Generated by Django 3.0.4 on 2020-05-14 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomwords', '0004_auto_20200514_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessione',
            name='timestamp_commento',
            field=models.IntegerField(default=0),
        ),
    ]
