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

ASK_DICT = None

def fill_ASK_DICT():
    global ASK_DICT
    ASK_DICT = dict()
    fill_ASK_DICT_with_model(Company)
    fill_ASK_DICT_with_model(TaxBase)

    print(ASK_DICT)


def fill_ASK_DICT_with_model(model):
    global ASK_DICT
    for field in model._meta.get_fields():
        if isinstance(field, models.OneToOneRel):
            continue

        name = field.name
        if model.__name__ != 'Company':
            name = model.__name__ + '__' + name

        ASK_DICT[name] = {
            'human': field.verbose_name[:40],
            'machine': field.name,
            'suggestions': [],
        }

        if isinstance(field, models.BooleanField):
            ASK_DICT[name].update({
                'type': 'bool',
                'suggestions': [
                    {'id': 1, 'name': 'True'},
                    {'id': 2, 'name': 'False'}
                ],
            })

        if isinstance(field, models.IntegerField) or isinstance(field, models.FloatField):
            ASK_DICT[name].update({
                'type': 'number',
            })

        if isinstance(field, models.DateField):
            ASK_DICT[name].update({
                'type': 'date',
            })



class Company(models.Model):
    # primary key
    inn = models.IntegerField("ИНН", primary_key=True)

    # main fields
    date_create = models.DateField("дата создания компании", null=True)
    still_alive = models.BooleanField("еще существует?", null=False, default=True)
    is_ip = models.BooleanField("является ИП", null=True)

    # location
    location_code = models.IntegerField("код региона", null=True)


class EmployeeNum(models.Model):
    inn = models.OneToOneField(Company, on_delete=models.CASCADE)
    employee_num = models.IntegerField("количество работников", null=True)


class CompanyLocation(models.Model):
    inn = models.OneToOneField(Company, on_delete=models.CASCADE)


for hname in LOCATION_TYPES:
    CompanyLocation.add_to_class(hname, models.CharField(name=hname, max_length=40, null=True))


TAX_TYPES = {
 'Задолженность и перерасчеты по ОТМЕНЕННЫМ НАЛОГАМ  '
 'и сборам и иным обязательным платежам  (кроме ЕСН, страх. Взносов)': 'tax_atribute_0',
 'Транспортный налог': 'tax_atribute_1',
 'Водный налог': 'tax_atribute_2',
 'Налог, взимаемый в связи с  применением упрощенной  '
 'системы налогообложения': 'tax_atribute_3',
 'Налог на добавленную стоимость': 'tax_atribute_4',
 'Земельный налог': 'tax_atribute_5',
 'Акцизы, всего': 'tax_atribute_6',
 'НЕНАЛОГОВЫЕ ДОХОДЫ, администрируемые налоговыми органами': 'tax_atribute_7',
 'Единый налог на вмененный доход для отдельных видов  '
 'деятельности': 'tax_atribute_8',
 'Налог на добычу полезных ископаемых': 'tax_atribute_9',
 'Страховые и другие взносы на обязательное пенсионное '
 'страхование, зачисляемые в Пенсионный фонд Российской Федерации': 'tax_atribute_10',
 'Страховые взносы на обязательное медицинское страхование'
 ' работающего населения, зачисляемые в бюджет Федерального'
 ' фонда обязательного медицинского страхования': 'tax_atribute_11',
 'Налог на имущество организаций': 'tax_atribute_12',
 'Налог на прибыль': 'tax_atribute_13',
 'Торговый сбор': 'tax_atribute_14',
 'Налог на доходы физических лиц': 'tax_atribute_15',
 'Единый сельскохозяйственный налог': 'tax_atribute_16',
 'Сборы за пользование объектами животного мира  и за '
 'пользование объектами ВБР': 'tax_atribute_17',
 'Страховые взносы на обязательное социальное страхование'
 ' на случай временной нетрудоспособности и в связи с материнством': 'tax_atribute_18'
}


class TaxBase(models.Model):
    inn = models.OneToOneField(Company, on_delete=models.CASCADE)
    date_fns = models.DateField('время добавления ФНСом', null=True)


for hname, pyname in TAX_TYPES.items():
    TaxBase.add_to_class(pyname, models.FloatField(name=hname, default=0))
