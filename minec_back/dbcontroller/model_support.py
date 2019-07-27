from django.db import models
from dbcontroller.models import \
    TaxBase, Company, Alive, EmployeeNum, BaseIncome, OKVED, LoadDates, InnStore
from dbcontroller.models_constants import *
from dbcontroller.description_dict import get_description


USED_MODELS = [Company, Alive, TaxBase, EmployeeNum, BaseIncome, OKVED, LoadDates, InnStore]


def create_ASK_DICT():
    ASK_DICT = dict()
    for model in USED_MODELS:
        fill_ASK_DICT_with_model(model, ASK_DICT)
    return ASK_DICT


def create_base_to_fields_dicts():
    ask_dict = create_ASK_DICT()
    b2f = dict()
    f2b = dict()
    for field, item in ask_dict.items():
        table = item['table']
        f2b[field] = item['table']
        if table not in b2f.keys():
            b2f[table] = []
        b2f[table].append(field)
    return b2f, f2b


def create_TAX_DICT():
    TAX_DICT = dict()
    for i, field in enumerate(TaxBase._meta.get_fields()):
        TAX_DICT[field.verbose_name] = field.name
    return TAX_DICT


def iterate_over_visible_fields(model=None):
    all_models = [model] if model is not None else USED_MODELS
    for cur_model in all_models:
        for field in cur_model._meta.get_fields():
            if isinstance(field, models.OneToOneRel) or\
                    isinstance(field, models.ForeignKey) or\
                    isinstance(field, models.ManyToOneRel) or\
                    isinstance(field, models.ManyToManyField) or\
                    isinstance(field, models.ManyToManyRel):
                continue

            if field.name.lower() == 'id':
                continue

            if field.name.lower() == 'inn' and not model.__name__ == 'Company':
                continue

            if field.verbose_name.startswith(TECH_FILED):
                continue

            yield field


def fill_ASK_DICT_with_model(model, ASK_DICT):
    for field in iterate_over_visible_fields(model):

        name = field.name
        if model.__name__ != 'LoadDates':
            name = model.__name__ + '__' + name
        name = name.lower()

        ASK_DICT[name] = {
            'table': model.__name__,
            'human': field.verbose_name[:60],
            'machine': name,
            'description': get_description(field),
            'sign': [{'value': 'none', 'name': '---'}],
            'type': 'undefined',
            'suggestions': [],
        }

        if isinstance(field, models.TextField):
            ASK_DICT[name].update({
                'type': 'text',
                'sign': [{'value': 'eq', 'name': '='}],
            })

        if isinstance(field, models.BooleanField):
            ASK_DICT[name].update({
                'type': 'bool',
                'sign': [
                    {'value': 'eq', 'name': '='},
                    {'value': 'range', 'name': 'одно из'},
                ],
            })

        if isinstance(field, models.IntegerField) or isinstance(field, models.FloatField):
            ASK_DICT[name].update({
                'type': 'number',
                'sign': [
                    {'value': 'range', 'name': 'одно из'},
                    {'value': 'eq', 'name': '='},
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
                    {'value': 'eq', 'name': '='},
                    {'value': 'gt', 'name': '>'},
                    {'value': 'lt', 'name': '<'},
                    {'value': 'gte', 'name': '>='},
                    {'value': 'lte', 'name': '<='},
                ],
            })

        if field.choices is not None and len(field.choices) > 0:
            ASK_DICT[name].update({
                'type': 'multy',
                'sign': [
                    {'value': 'eq', 'name': '='},
                    {'value': 'range', 'name': 'одно из'}
                ],
                'suggestions': [{'name': x[1], 'value': x[0]} for x in field.choices],
                'machine_mapper': {x[0]: x[1] for x in field.choices},
            })


def fakeFill():
    import datetime

    loadDate1 = LoadDates(date=datetime.datetime.strptime('01.01.1970', '%d.%m.%Y'))
    loadDate1.save()
    loadDate2 = LoadDates(
        date=datetime.datetime.strptime('01.01.2019', '%d.%m.%Y')
    )
    loadDate2.save()

    company1 = Company(
        inn='10',
        is_ip=True,
        owner_name='Michael',
    )
    company1.save()
    company1.upd_date.add(loadDate1, loadDate2)

    company2 = Company(
        inn='11',
        is_ip=False,
        short_title='ООО М(ФТИ)'
    )
    company2.save()
    company2.upd_date.add(loadDate1, loadDate2)

    for i, comp in enumerate([company1, company2]):
        for j, date in enumerate([loadDate1, loadDate2]):
            emp = EmployeeNum(
                _company=comp,
                employee_num=100 * i + 10 * j
            )
            emp.save()
            emp.upd_date.add(date)

    print(LoadDates.objects.filter(employeenum__upd_date=loadDate1).values(
        'date', 'employeenum__employee_num'
    ))
    print()


def del_all():
    Company.objects.all().delete()
    LoadDates.objects.all().delete()