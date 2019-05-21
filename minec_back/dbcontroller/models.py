from django.db import models


LOCATION_TYPES ={
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
TECH_FILED = "technical filed"


def create_ASK_DICT():
    ASK_DICT = dict()
    fill_ASK_DICT_with_model(Company, ASK_DICT)
    fill_ASK_DICT_with_model(Alive, ASK_DICT)
    fill_ASK_DICT_with_model(TaxBase, ASK_DICT)
    fill_ASK_DICT_with_model(EmployeeNum, ASK_DICT)

    print(ASK_DICT.keys())
    return ASK_DICT


def create_TAX_DICT():
    TAX_DICT = dict()
    for i, field in enumerate(TaxBase._meta.get_fields()):
        TAX_DICT[field.verbose_name] = field.name
    return TAX_DICT


def fill_ASK_DICT_with_model(model, ASK_DICT):
    for i, field in enumerate(model._meta.get_fields()):
        if isinstance(field, models.OneToOneRel):
            continue

        if field.name.lower() == 'id':
            continue

        if field.name.lower() == 'inn' and not model.__name__ == 'Company':
            continue

        if field.verbose_name.startswith(TECH_FILED):
            continue

        name = field.name
        if model.__name__ != 'Company':
            name = model.__name__ + '__' + name
        name = name.lower()

        ASK_DICT[name] = {
            'human': field.verbose_name[:50],
            'machine': name,
            'sign': [{'value': 'none', 'name': '---'}],
            'suggestions': [],
        }

        if isinstance(field, models.BooleanField):
            ASK_DICT[name].update({
                'type': 'multi',
                'sign': [{'value': 'range', 'name': 'одно из'}],
                'suggestions': [
                    {'id': 1, 'name': 'True'},
                    {'id': 2, 'name': 'False'}
                ],
            })

        if isinstance(field, models.IntegerField) or isinstance(field, models.FloatField):
            ASK_DICT[name].update({
                'type': 'number',
                'sign': [
                    {'value': 'range', 'name': 'одно из'},
                    {'value': 'gt', 'name': '>'},
                    {'value': 'lt', 'name': '<'},
                    {'value': 'gte', 'name': '>='},
                    {'value': 'lte', 'name': '<='},
                ],
            })

        if isinstance(field, models.DateField):
            ASK_DICT[name].update({
                'type': 'date',
                'sign': [
                    {'value': 'range', 'name': 'одно из'},
                    {'value': 'gt', 'name': '>'},
                    {'value': 'lt', 'name': '<'},
                    {'value': 'gte', 'name': '>='},
                    {'value': 'lte', 'name': '<='},
                ],
            })


class Company(models.Model):
    # primary key
    inn = models.IntegerField("ИНН", primary_key=True)

    # main fields
    date_create = models.DateField("дата создания компании", null=True)
    is_ip = models.BooleanField("является ИП", null=True)

    # location
    location_code = models.IntegerField("код региона", null=True)


class Alive(models.Model):
    inn = models.OneToOneField(Company, on_delete=models.CASCADE)
    date_created = models.DateField("дата добавления в базу", null=False)
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
