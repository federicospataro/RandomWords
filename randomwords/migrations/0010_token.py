# Generated by Django 3.0.4 on 2020-05-22 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomwords', '0009_sessione_ip'),
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('token', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('tipo', models.IntegerField()),
                ('data', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]