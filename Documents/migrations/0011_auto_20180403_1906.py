# Generated by Django 2.0.3 on 2018-04-03 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Documents', '0010_auto_20180401_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentcopy',
            name='date',
            field=models.DateTimeField(default='2018-04-03 19:06'),
        ),
        migrations.AlterField(
            model_name='documentcopy',
            name='returning_date',
            field=models.DateTimeField(default='2018-04-03 19:06'),
        ),
    ]