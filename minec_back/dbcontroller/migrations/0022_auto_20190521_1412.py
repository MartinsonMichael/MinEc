# Generated by Django 2.1.7 on 2019-05-21 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbcontroller', '0021_auto_20190521_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alive',
            name='life_duration_years',
            field=models.IntegerField(verbose_name='продолжительность существования (лет)'),
        ),
    ]