# Generated by Django 2.1.7 on 2019-05-28 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbcontroller', '0026_auto_20190521_2000'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='owner_name',
            field=models.TextField(max_length=100, null=True, verbose_name='имя владельца (для ИП)'),
        ),
        migrations.AddField(
            model_name='company',
            name='short_title',
            field=models.TextField(max_length=100, null=True, verbose_name='краткое название (не для ИП)'),
        ),
    ]
