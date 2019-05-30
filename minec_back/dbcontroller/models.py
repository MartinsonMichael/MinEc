from django.db import models
from collections import defaultdict

LOCATION_TYPES = {
    'город',
    'городской округ',
    'дачный поселок',
    'деревня',
    'железнодорожная станция',
    'квартал',
    'край',
    'область',
    'поселение',
    'поселок',
    'поселок городского типа',
    'рабочий поселок',
    'район',
    'республика',
    'село',
    'станция'
}
REGION_TYPES = defaultdict(lambda: 'НЕИЗВЕСТНО', {
 1: 'адыгея республика',
 2: 'башкортостан республика',
 3: 'бурятия республика',
 4: 'алтай республика',
 5: 'дагестан республика',
 6: 'ингушетия республика',
 7: 'кабардино-балкарская республика',
 8: 'калмыкия республика',
 9: 'карачаево-черкесская республика',
 10: 'карелия республика',
 11: 'коми республика',
 12: 'марий эл республика',
 13: 'мордовия республика',
 14: 'саха /якутия/ республика',
 15: 'северная осетия - алания республика',
 16: 'татарстан республика',
 17: 'тыва республика',
 18: 'удмуртская республика',
 19: 'хакасия республика',
 20: 'чеченская республика',
 21: 'чувашская республика - чувашия',
 22: 'алтайский край',
 23: 'краснодарский край',
 24: 'красноярский край',
 25: 'приморский край',
 26: 'ставропольский край',
 27: 'хабаровский край',
 28: 'амурская область',
 29: 'архангельская область',
 30: 'астраханская область',
 31: 'белгородская область',
 32: 'брянская область',
 33: 'владимирская область',
 34: 'волгоградская область',
 35: 'вологодская область',
 36: 'воронежская область',
 37: 'ивановская область',
 38: 'иркутская область',
 39: 'калининградская область',
 40: 'калужская область',
 41: 'камчатский край',
 42: 'кемеровская область',
 43: 'кировская область',
 44: 'костромская область',
 45: 'курганская область',
 46: 'курская область',
 47: 'ленинградская область',
 48: 'липецкая область',
 49: 'магаданская область',
 50: 'московская область',
 51: 'мурманская область',
 52: 'нижегородская область',
 53: 'новгородская область',
 54: 'новосибирская область',
 55: 'омская область',
 56: 'оренбургскаяобласть область',
 57: 'орловская область',
 58: 'пензенская область',
 59: 'пермский край',
 60: 'псковская область',
 61: 'ростовская область',
 62: 'рязанская область',
 63: 'самарская область',
 64: 'саратовская область',
 65: 'сахалинская область',
 66: 'свердловская область',
 67: 'смоленская область',
 68: 'тамбовская область',
 69: 'тверская область',
 70: 'томская область',
 71: 'тульская область',
 72: 'тюменская область',
 73: 'ульяновская область',
 74: 'челябинская область',
 75: 'забайкальский край',
 76: 'ярославская область',
 77: 'москва город',
 78: 'санкт-петербург город',
 79: 'еврейская автономная область',
 83: 'ненецкий автономный округ',
 86: 'ханты-мансийский автономный округ - югра автономный округ',
 87: 'чукотский автономный округ',
 89: 'ямало-ненецкий автономный округ',
 91: 'крым республика',
 92: 'севастополь город',
})
TECH_FILED = "technical filed"


class Company(models.Model):
    # primary key
    inn = models.IntegerField("ИНН", primary_key=True)

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
        default=REGION_TYPES[0]
    )


class Alive(models.Model):
    inn = models.OneToOneField(Company, on_delete=models.CASCADE)
    date_create = models.DateField("дата создания компании", null=True)
    date_add_to_base = models.DateField("дата добавления в базу", null=False)
    date_disappear = models.DateField("дата прекращения существования", null=True)
    still_alive = models.BooleanField("еще существует?", null=False, default=True)
    life_duration_years = models.IntegerField("продолжительность существования (лет)", null=False)
    still_not_found = models.BooleanField(TECH_FILED, null=True)


class EmployeeNum(models.Model):
    inn = models.OneToOneField(Company, on_delete=models.CASCADE)
    employee_num = models.IntegerField("количество работников", null=True)


class TaxBase(models.Model):
    inn = models.OneToOneField(Company, on_delete=models.CASCADE)
    date_fns = models.DateField('время добавления ФНСом информации о налогах', null=True)

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


class BaseIncome(models.Model):
    inn = models.OneToOneField(Company, on_delete=models.CASCADE)
    income = models.FloatField('доход')
    outcome = models.FloatField('расход')