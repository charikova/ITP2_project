# Generated by Django 2.0.3 on 2018-03-31 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Documents', '0010_auto_20180331_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentcopy',
            name='date',
            field=models.DateTimeField(default='2018-03-31 12:16'),
        ),
        migrations.AlterField(
            model_name='documentcopy',
            name='returning_date',
            field=models.DateTimeField(default='2018-03-31 12:16'),
        ),
    ]
