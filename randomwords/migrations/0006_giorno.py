# Generated by Django 3.0.4 on 2020-05-15 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('randomwords', '0005_sessione_timestamp_commento'),
    ]

    operations = [
        migrations.CreateModel(
            name='Giorno',
            fields=[
                ('Cod_Estrazione', models.AutoField(primary_key=True, serialize=False)),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('Cod_Cont', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='randomwords.Contenuto')),
            ],
        ),
    ]
