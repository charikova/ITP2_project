# Generated by Django 2.0.1 on 2018-02-03 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Documents', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentcopy',
            name='date',
            field=models.DateTimeField(default='2018-02-03 15:17'),
        ),
        migrations.AlterField(
            model_name='documentcopy',
            name='fine_price',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='documentcopy',
            name='returning_date',
            field=models.DateTimeField(default='2018-02-03 15:17'),
        ),
    ]
