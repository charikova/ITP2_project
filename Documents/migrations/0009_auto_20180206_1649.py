# Generated by Django 2.0.1 on 2018-02-06 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Documents', '0008_auto_20180205_2247'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='is_reference',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='documentcopy',
            name='date',
            field=models.DateTimeField(default='2018-02-06 16:49'),
        ),
        migrations.AlterField(
            model_name='documentcopy',
            name='returning_date',
            field=models.DateTimeField(default='2018-02-06 16:49'),
        ),
    ]