from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Tuple
from sqlalchemy import Column, String, Boolean, Date, Integer, Float
from sqlalchemy_utils.types.choice import ChoiceType, Choice
from sqlalchemy import func as sqla_func

from dbcontroller.model_constants import \
    COLUMN_TYPE_TO_NAME, \
    get_TABLES_COLUMN_MACHINE_TO_HUMAN_NAME, \
    get_TABLES_COLUMN_MACHINE_TO_HUMAN_DESCRIPTION, TABLES_COLUMN_MACHINE_TO_HUMAN_NAME
from dbcontroller.models import USED_TABLES, get_upd_date_list


def get_type_description(column: Column) -> str:
    if isinstance(column.type, Integer):
        return 'Это целочисленное числовое поле. Для неинтервальных ' \
               'сравнений (<, >, =, >=, <=) нужно ввести одно целое число. ' \
               'Возможны интервальные сравнения, для этого введите диапазон в формате:' \
               '"xxx-xx", где x это цифры. Можно вводить несколько диапазонов через запятую ' \
               'и отдельные числа. Например "12,34-40,60-80". Пробелы не допускаются.'

    if isinstance(column.type, Float):
        return 'Это вещественное числовое поле. Для неинтервальных ' \
               'сравнений (<, >, =, >=, <=) нужно ввести одно число (точка как разделитель дробной части). ' \
               'Возможны интервальные сравнения, для этого введите диапазон в формате:' \
               '"xxx.xx-xx.x", где x это цифры. Можно вводить несколько диапазонов через запятую ' \
               'и отдельные числа. Например "12.43,34.0-40.0,60.5-80.5,123". Пробелы не допускаются.'

    if isinstance(column.type, Boolean):
        return 'Это булевое поле. Оно поддерживает только точное сравнение (=) и может сравниваться с ' \
               'истинностью (выберете "Да") и ложью (выперете "Нет")'

    if isinstance(column.type, Date):
        return 'Это поле формата даты. Для неинтервальных ' \
               'сравнений (<, >, =, >=, <=) нужно ввести одну дату в формате "ДД.ММ.ГГГГ". ' \
               'Возможны интервальные сравнения, для этого введите диапазон в формате:' \
               '"ДД.ММ.ГГГГ-ДД.ММ.ГГГГ", где x это цифры. Можно вводить несколько диапазонов через запятую ' \
               'и отдельные даты. Например "01.01.1970-01.12.1970,01.11.2019". Пробелы не допускаются.'

    if isinstance(column.type, ChoiceType):
        return 'Это поле c вариантами выбора значений. ' \
               'Выберете нужное количество значений, к ним будет примененно ИЛИ.'

    if isinstance(column.type, String):
        return 'Это текстовое поле. Оно поддеживает только прямые (=) сравнения. ' \
               'Если при выборе этого поля в секции фильтров не появились автоподсказки ' \
               'с возможными значениями, то это поле имеент слишком много различных данных ' \
               'и им не рекомендуется пользоваться.\n' \
               'Если же опции появились выберете нужное количество нужных опций, к ним будет применено "ИЛИ"'

    return "Формат поля неизвестен."


def get_description(column: Column) -> Dict[str, str]:
    return {
        'name_description': get_TABLES_COLUMN_MACHINE_TO_HUMAN_DESCRIPTION(column.name),
        'type_description': get_type_description(column),
    }


def get_signs_for_column(column: Column) -> List[Dict[str, str]]:
    if isinstance(column.type, String) or isinstance(column.type, Boolean) or column.name == 'upd_date':
        return [
            {'value': 'eq', 'name': '='},
        ]

    if isinstance(column.type, Float) or isinstance(column.type, Integer) or isinstance(column.type, Date):
        return [
            {'value': 'range', 'name': 'одно из'},
            {'value': 'eq', 'name': '='},
            {'value': 'gt', 'name': '>'},
            {'value': 'lt', 'name': '<'},
            {'value': 'gte', 'name': '>='},
            {'value': 'lte', 'name': '<='},
         ]

    if isinstance(column.type, ChoiceType):
        return [
            {'value': 'eq', 'name': '='},
            {'value': 'range', 'name': 'одно из'},
         ]


def serializer(x):
    if isinstance(x, datetime):
        return str(x.day) + '.' + str(x.month) + '.' + str(x.year)
    if isinstance(x, Choice):
        return x.code
    return x


def get_suggestions_for_column(column: Column) -> List[Dict[str, str]]:
    if column.name == 'upd_date':

        # FIXME
        print(get_upd_date_list())
        def s(x):
            return str(x.day) + '.' + str(x.month) + '.' + str(x.year)
        upd_date_suggestions = [
            {'text': s(value[0]), 'value': s(value[0])} for value in get_upd_date_list()
        ]
        print(f'upd_date_suggestions : {upd_date_suggestions}')
        return upd_date_suggestions
    if not isinstance(column.type, ChoiceType):
        return []
    return [
        {'text': name, 'value': value} for name, value in column.type.choices
    ]


def get_column_text_type(column: Column) -> str:
    if column.name == 'upd_date':
        return 'multi'
    return COLUMN_TYPE_TO_NAME[type(column.type)]


def create_AskDict() -> Dict[str, Dict[str, Any]]:
    ask_dict = {}
    for table in USED_TABLES:
        for column in table.__table__.columns:
            ask_dict[column.name] = {
                'machine_name': column.name.lower(),
                'table_name': column.table.name.lower(),
                'human_name': get_TABLES_COLUMN_MACHINE_TO_HUMAN_NAME(column.name.lower()),
                'human_description': get_description(column),
                'sign': get_signs_for_column(column),
                'suggestions': get_suggestions_for_column(column),
                'type': get_column_text_type(column),
            }
    ask_dict.update(__update_AskDict_with_Inn())
    return ask_dict


def __update_AskDict_with_Inn() -> Dict[str, Any]:
    ask_dict_updated = {}
    for table in USED_TABLES:
        for column in table.__table__.columns:
            if column.name != 'inn' and column.name != 'upd_date':
                continue
            ask_dict_updated[column.name.lower() + '_' + column.table.name.lower()] = {
                'machine_name': column.name.lower(),
                'table_name': column.table.name.lower(),
                'human_name': get_TABLES_COLUMN_MACHINE_TO_HUMAN_NAME(column.name.lower()),
                'human_description': get_description(column),
                'sign': get_signs_for_column(column),
                'suggestions': get_suggestions_for_column(column),
                'type': get_column_text_type(column),
            }
    return ask_dict_updated


def __create_column_mapper() -> Dict[str, Column]:
    column_mapper = {}
    for table in USED_TABLES:
        for column in table.__table__.columns:
            column_name_for_mapper = column.name
            if column.name in {'inn', 'upd_date'}:
                column_name_for_mapper += '_' + column.table.name.lower()
                if column.table.name.lower() == 'company':
                    column_mapper[column.name.lower()] = column
            column_mapper[column_name_for_mapper] = column
    return column_mapper


COLUMN_MAPPER = __create_column_mapper()


# print()
# print(f'COLUMN_MAPPER {COLUMN_MAPPER.keys()}')
# print()
# print(f'create_AskDict().keys() {create_AskDict().keys()}')
# print()


AGGREGATION_NAME_TO_FUNC = {
    'max': lambda x: sqla_func.max(x),
    'avg': lambda x: sqla_func.avg(x),
    'sum': lambda x: sqla_func.sum(x),
    'count': lambda x: sqla_func.count(x),
}


AGGREGATION_NAME_TO_HUMAN = defaultdict(lambda: '', {
    'sum': 'Сумма',
    'avg': 'Среднее',
    'count': 'Колиество',
    'max': 'Максимум',
})


def get_human_headers(column_list: List[Dict[str, Any]], aggregation: List[Dict[str, Any]]) -> List[str]:
    aggregate_column_names = [x['column_name'] for x in aggregation]
    aggregate_column_func = [x['column_aggregate_func'] for x in aggregation]
    cur_index = 0
    human_headers = []
    print(column_list)
    print(aggregation)
    for index, column_dict in enumerate(column_list):
        machine_name = column_dict['column_name']
        human_headers.append('')
        if machine_name in aggregate_column_names:
            human_headers[-1] += AGGREGATION_NAME_TO_HUMAN[aggregate_column_func[cur_index]] + ' '
            cur_index += 1
        human_headers[-1] += TABLES_COLUMN_MACHINE_TO_HUMAN_NAME[machine_name]

    return human_headers


def __create_sqla_aggregation_expression(aggregation: List[str]):
    return AGGREGATION_NAME_TO_FUNC[aggregation[1]](COLUMN_MAPPER[aggregation[0]])


def create_sqla_filter_expression(filters: List[Any]) -> List[Any]:
    pass
