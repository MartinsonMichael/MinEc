from .models import *

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


def fill_ASK_DICT_with_model(model, ASK_DICT):
    for i, field in enumerate(model._meta.get_fields()):
        if isinstance(field, models.OneToOneRel) or\
                isinstance(field, models.ForeignKey) or\
                isinstance(field, models.ManyToOneRel):
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
            'table': model.__name__,
            'human': field.verbose_name[:60],
            'machine': name,
            'sign': [{'value': 'none', 'name': '---'}],
            'suggestions': [],
        }

        if isinstance(field, models.BooleanField):
            ASK_DICT[name].update({
                'type': 'bool',
                'sign': [{'value': 'eq', 'name': '='}],
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

        if field.choices is not None and len(field.choices) > 0:
            ASK_DICT[name].update({
                'type': 'multy',
                'sign': [{'value': 'range', 'name': 'одно из'}],
                'suggestions': field.choices,
            })

