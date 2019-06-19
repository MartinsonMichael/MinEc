# Generated by Django 2.1.7 on 2019-06-19 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbcontroller', '0002_auto_20190618_0027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='federal_name',
            field=models.TextField(choices=[(0, 'Приволжский федеральный округ'), (1, 'Северо-Западный федеральный округ'), (2, 'Дальневосточный федеральный округ'), (3, 'Северо-Кавказский федеральный округ'), (4, 'Центральный федеральный округ'), (5, 'Южный федеральный округ'), (6, 'Уральский федеральный округ'), (7, 'Сибирский федеральный округ')], default='НЕИЗВЕСТНО', max_length=50, verbose_name='федеральный округ'),
        ),
    ]
