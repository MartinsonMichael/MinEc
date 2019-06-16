from django.db import models
from dbcontroller.models_constants import *


class ScheduleTable(models.Model):
    date = models.DateField(null=False)
    type = models.TextField(
        choices=[
            (0, 'NONE'),
            (1, 'load'),
            (2, 'unzip'),
            (3, 'add'),
            (4, 'done'),
        ],
        default='NONE',
        null=False,
    )
    zip_file_name = models.TextField(max_length=30, null=True)
    base_name = models.TextField(max_length=30, null=False)
    file_name = models.TextField(max_length=200, null=True)


class Company(models.Model):
    # primary key
    inn = models.TextField("ИНН", max_length=20, null=True, unique=True)

    # main fields
    is_ip = models.BooleanField("является ИП", null=True)
    # title = models.TextField("название (не для ИП)", null=True, max_length=100)
    short_title = models.TextField("краткое название (не для ИП)", null=True, max_length=100)
    owner_name = models.TextField("имя владельца (для ИП)", null=True, max_length=100)

    # location
    location_code = models.IntegerField("код региона", null=True)
    region_name = models.TextField(
        "Название региона",
        choices=[(x, y) for (x, y) in REGION_TYPES.items()],
        default=REGION_TYPES[0],
        null=True,
    )
    federal_name = models.TextField(
        verbose_name="федеральный округ",
        max_length=50,
        choices=[
            ({y: x for x, y in REGION_TYPES.items()}[reg], fed)
            for reg, fed in REGION_TO_FEDERAL.items()
        ],
        default="НЕИЗВЕСТНО",
    )


class Alive(models.Model):
    _company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date_create = models.DateField("дата создания компании", null=True)
    date_add_to_base = models.DateField("дата добавления в базу", null=True)
    date_disappear = models.DateField("дата прекращения существования", null=True)
    still_alive = models.BooleanField("еще существует?", null=False, default=True)
    life_duration_years = models.IntegerField("продолжительность существования (лет)", null=True)
    still_not_found = models.BooleanField(TECH_FILED, null=True)


class OKVED(models.Model):
    _company = models.ForeignKey(Company, on_delete=models.CASCADE)
    code = models.TextField(verbose_name='Код ОКВЭД', max_length=21, null=True)
    code_name = models.TextField(verbose_name='Название ОКВЭД', max_length=160, null=True)
    is_prime = models.BooleanField(verbose_name='Основное ОКВЭД?', null=True)

    class Meta:
        unique_together = ('code', '_company')


class EmployeeNum(models.Model):
    _company = models.OneToOneField(Company, on_delete=models.CASCADE)
    employee_num = models.IntegerField("количество работников", null=True)


class TaxBase(models.Model):
    _company = models.OneToOneField(Company, on_delete=models.CASCADE)
    date = models.DateField(verbose_name='дата помещения в базу', null=False)

    tax_atribute_0 = models.FloatField(
        verbose_name='Задолженность и перерасчеты по ОТМЕНЕННЫМ НАЛОГАМ'
                     '  и сборам и иным обязательным платежам  (кроме ЕСН, страх. Взносов)',
        default=0)
    tax_atribute_1 = models.FloatField(verbose_name='Транспортный налог', default=0)
    tax_atribute_2 = models.FloatField(verbose_name='Водный налог', default=0)
    tax_atribute_3 = models.FloatField(
        verbose_name='Налог, взимаемый в связи с  применением упрощенной  '
                     'системы налогообложения', default=0)
    tax_atribute_4 = models.FloatField(verbose_name='Налог на добавленную стоимость', default=0)
    tax_atribute_5 = models.FloatField(verbose_name='Земельный налог', default=0)
    tax_atribute_6 = models.FloatField(verbose_name='Акцизы, всего', default=0)
    tax_atribute_7 = models.FloatField(verbose_name='НЕНАЛОГОВЫЕ ДОХОДЫ, '
                                                    'администрируемые налоговыми органами',
                                       default=0)
    tax_atribute_8 = models.FloatField(verbose_name='Единый налог на вмененный '
                                                    'доход для отдельных видов  деятельности',
                                       default=0)
    tax_atribute_9 = models.FloatField(verbose_name='Налог на добычу полезных ископаемых',
                                       default=0)
    tax_atribute_10 = models.FloatField(
        verbose_name='Страховые и другие взносы на обязательное пенсионное страхование,'
                     ' зачисляемые в Пенсионный фонд Российской Федерации',
        default=0)
    tax_atribute_11 = models.FloatField(
        verbose_name='Страховые взносы на обязательное медицинское страхование '
                     'работающего населения, зачисляемые в бюджет Федерального фонда '
                     'обязательного медицинского страхования',
        default=0)
    tax_atribute_12 = models.FloatField(verbose_name='Налог на имущество организаций',
                                        default=0)
    tax_atribute_13 = models.FloatField(verbose_name='Налог на прибыль', default=0)
    tax_atribute_14 = models.FloatField(verbose_name='Торговый сбор', default=0)
    tax_atribute_15 = models.FloatField(verbose_name='Налог на доходы физических лиц',
                                        default=0)
    tax_atribute_16 = models.FloatField(verbose_name='Единый сельскохозяйственный налог',
                                        default=0)
    tax_atribute_17 = models.FloatField(
        verbose_name='Сборы за пользование объектами животного мира  и за пользование '
                     'объектами ВБР', default=0)
    tax_atribute_18 = models.FloatField(
        verbose_name='Страховые взносы на обязательное социальное страхование на случай'
                     ' временной нетрудоспособности и в связи с материнством',
        default=0)
    tax_atribute_19 = models.FloatField(
        verbose_name='Утилизационный сбор',
        default=0)
    tax_atribute_20 = models.FloatField(
        verbose_name='Налог на игорный',
        default=0)
    tax_atribute_21 = models.FloatField(
        verbose_name='Государственная пошлина',
        default=0)


class BaseIncome(models.Model):
    _company = models.OneToOneField(Company, on_delete=models.CASCADE)
    income = models.FloatField('доход')
    outcome = models.FloatField('расход')





