# Generated by Django 2.1.7 on 2019-05-16 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbcontroller', '0017_auto_20190516_1331'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taxbase',
            name='Акцизы, всего',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Водный налог',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Единый налог на вмененный доход для отдельных видов  деятельности',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Единый сельскохозяйственный налог',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Задолженность и перерасчеты по ОТМЕНЕННЫМ НАЛОГАМ  и сборам и иным обязательным платежам  (кроме ЕСН, страх. Взносов)',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Земельный налог',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='НЕНАЛОГОВЫЕ ДОХОДЫ, администрируемые налоговыми органами',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Налог на добавленную стоимость',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Налог на добычу полезных ископаемых',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Налог на доходы физических лиц',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Налог на имущество организаций',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Налог на прибыль',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Налог, взимаемый в связи с  применением упрощенной  системы налогообложения',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Сборы за пользование объектами животного мира  и за пользование объектами ВБР',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Страховые взносы на обязательное медицинское страхование работающего населения, зачисляемые в бюджет Федерального фонда обязательного медицинского страхования',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Страховые взносы на обязательное социальное страхование на случай временной нетрудоспособности и в связи с материнством',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Страховые и другие взносы на обязательное пенсионное страхование, зачисляемые в Пенсионный фонд Российской Федерации',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Торговый сбор',
        ),
        migrations.RemoveField(
            model_name='taxbase',
            name='Транспортный налог',
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_0',
            field=models.FloatField(default=0, verbose_name='Задолженность и перерасчеты по ОТМЕНЕННЫМ НАЛОГАМ  и сборам и иным обязательным платежам  (кроме ЕСН, страх. Взносов)'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_1',
            field=models.FloatField(default=0, verbose_name='Транспортный налог'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_10',
            field=models.FloatField(default=0, verbose_name='Страховые и другие взносы на обязательное пенсионное страхование, зачисляемые в Пенсионный фонд Российской Федерации'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_11',
            field=models.FloatField(default=0, verbose_name='Страховые взносы на обязательное медицинское страхование работающего населения, зачисляемые в бюджет Федерального фонда обязательного медицинского страхования'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_12',
            field=models.FloatField(default=0, verbose_name='Налог на имущество организаций'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_13',
            field=models.FloatField(default=0, verbose_name='Налог на прибыль'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_14',
            field=models.FloatField(default=0, verbose_name='Торговый сбор'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_15',
            field=models.FloatField(default=0, verbose_name='Налог на доходы физических лиц'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_16',
            field=models.FloatField(default=0, verbose_name='Единый сельскохозяйственный налог'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_17',
            field=models.FloatField(default=0, verbose_name='Сборы за пользование объектами животного мира  и за пользование объектами ВБР'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_18',
            field=models.FloatField(default=0, verbose_name='Страховые взносы на обязательное социальное страхование на случай временной нетрудоспособности и в связи с материнством'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_2',
            field=models.FloatField(default=0, verbose_name='Водный налог'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_3',
            field=models.FloatField(default=0, verbose_name='Налог, взимаемый в связи с  применением упрощенной  системы налогообложения'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_4',
            field=models.FloatField(default=0, verbose_name='Налог на добавленную стоимость'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_5',
            field=models.FloatField(default=0, verbose_name='Земельный налог'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_6',
            field=models.FloatField(default=0, verbose_name='Акцизы, всего'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_7',
            field=models.FloatField(default=0, verbose_name='НЕНАЛОГОВЫЕ ДОХОДЫ, администрируемые налоговыми органами'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_8',
            field=models.FloatField(default=0, verbose_name='Единый налог на вмененный доход для отдельных видов  деятельности'),
        ),
        migrations.AddField(
            model_name='taxbase',
            name='tax_atribute_9',
            field=models.FloatField(default=0, verbose_name='Налог на добычу полезных ископаемых'),
        ),
    ]
