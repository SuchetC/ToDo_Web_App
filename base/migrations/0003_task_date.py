# Generated by Django 4.1.5 on 2023-02-17 08:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20210322_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
