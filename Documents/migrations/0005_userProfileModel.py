# Generated by Django 2.0.1 on 2018-02-03 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Documents', '0004_auto_20180131_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentcopy',
            name='date',
            field=models.DateTimeField(default='2018-02-03 12:16'),
        ),
        migrations.AlterField(
            model_name='documentcopy',
            name='price',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='documentcopy',
            name='returning_date',
            field=models.DateTimeField(default='2018-02-03 12:16'),
        ),
    ]