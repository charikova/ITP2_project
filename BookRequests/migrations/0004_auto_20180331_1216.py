# Generated by Django 2.0.3 on 2018-03-31 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BookRequests', '0003_outstandingrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outstandingrequest',
            name='timestamp',
            field=models.DateTimeField(default=None),
        ),
    ]