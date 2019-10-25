import datetime
import itertools
from typing import Dict, List, Any, Tuple, Type, Set, Union
import sqlalchemy as sqla
import typing

from traitlets import Integer

from dbcontroller.model_support import \
    create_AskDict, \
    COLUMN_MAPPER, \
    get_human_headers, \
    __create_sqla_aggregation_expression
from dbcontroller.models import Company, EmployeeNum, TaxBase, BaseIncome, USED_TABLES, DateList
from dbcontroller.session_contoller import session_scope

SPLIT_SYMBOL = '#'
AGGREGATE_KEY = 'aggregate'
GROUP_KEY = 'group_by'
FILTER_KEY = 'filter'
ASK_DICT = create_AskDict()
ParsedQuery = Dict[str, List[Dict[str, Any]]]


def parse_value(value, case):
    '''
    :return list of or values
    '''
    value = value[:-1]

    if case['type'] == 'bool':
        return [bool(value[0])]

    if case['type'] == 'multi':
        if case['machine_name'] == 'upd_date':
            value = [datetime.datetime.strptime(x, '%d.%m.%Y') for x in value]
        else:
            mapper = case['suggestions']
            value = [[y['text'] for y in mapper if y['value'] == int(x)][0] for x in value]
        return value

    if case['type'] == 'number':
        value = value[0].split(',')
        for i in range(len(value)):
            if '-' in value[i]:
                value[i] = tuple(sorted(list(map(float, value[i].split('-')))))
            else:
                value[i] = float(value[i])
        return value

    if case['type'] == 'date':
        value = value[0].split(',')
        for i in range(len(value)):
            if '-' in value[i]:
                buf = value[i].split('-')
                value[i] = sorted((
                    datetime.datetime.strptime(buf[0], '%d.%m.%Y'),
                    datetime.datetime.strptime(buf[1], '%d.%m.%Y')
                ))
            else:
                value[i] = datetime.datetime.strptime(value[i], '%d.%m.%Y')
        return value


def extract_params(options_dict: Dict[str, List[str]]) -> ParsedQuery:
    text_query = {
        FILTER_KEY: [],
        GROUP_KEY: [],
        AGGREGATE_KEY: [],
    }

    if len(get_tables_set(options_dict, {'aggregate', 'groupby'})) != 0:
        tables = list(get_tables_set(options_dict, {'aggregate', 'groupby'}))
    else:
        tables = list(get_tables_set(options_dict))
    if len(tables) == 0:
        tables = ['company']

    for key, value in options_dict.items():
        items = value[0].split(SPLIT_SYMBOL)
        if items[0] in {'inn', 'upd_date'}:
            items[0] = items[0] + '_' + tables[0]
        if key.startswith('filter'):
            text_query[FILTER_KEY].append({
                'column_name': items[0],
                'column_obj': COLUMN_MAPPER[items[0]],
                'sign': items[1],
                'value': parse_value(items[2:], ASK_DICT[items[0]]),
            })
        if key.startswith('aggregate'):
            text_query[AGGREGATE_KEY].append({
                'column_name': items[0],
                'column_obj': __create_sqla_aggregation_expression(items),
                'column_aggregate_func': items[1],
            })
        if key.startswith('groupby'):
            text_query[GROUP_KEY].append({
                'column_name': items[0],
                'column_obj': COLUMN_MAPPER[items[0]],
            })
    return text_query


# def table_separator(text_query: ParsedQuery) -> Dict[str, ParsedQuery]:
#     table_list_parsed_query = {}
#     for query_type in [AGGREGATE_KEY, FILTER_KEY, GROUP_KEY]:
#         for item in text_query[query_type]:
#             table_name = ASK_DICT[item['column_name']]['table_name']
#             if table_name not in table_list_parsed_query.keys():
#                 table_list_parsed_query[table_name] = {}
#             if query_type not in table_list_parsed_query[table_name].keys():
#                 table_list_parsed_query[table_name][query_type] = []
#             table_list_parsed_query[table_name][query_type].append(item)
#     return table_list_parsed_query


def column_determiner(text_query: ParsedQuery, tables: List[str]) -> List[Dict[str, Any]]:
    if len(text_query[AGGREGATE_KEY]) > 0 or len(text_query[GROUP_KEY]) > 0:
        return [
            *[item for item in text_query[AGGREGATE_KEY]],
            *[item for item in text_query[GROUP_KEY]],
        ]

    used_tables = tables
    for item in text_query[FILTER_KEY]:
        used_tables.append(ASK_DICT[item['column_name']]['table_name'])
    used_tables = set(used_tables)
    print(f'column_determiner -> used_tables: {used_tables}')

    if len(used_tables) == 0:
        used_tables.add('company')

    columns = []
    for column_name, info in ASK_DICT.items():
        if info['table_name'] in used_tables and (column_name != 'inn' and column_name != 'upd_date'):
            columns.append({
                'column_name': column_name,
                'column_obj': COLUMN_MAPPER[column_name],
            })
    print(f'column determiner -> columns : {columns}')
    return columns


def get_tables_set(options_dict: Dict[str, List[str]], only_type: Set[str] = None) -> Set[str]:
    if only_type is None:
        only_type = {'filter', 'groupby', 'aggregate'}
    tables = set()
    for key, value in options_dict.items():
        print(key)
        if key == 'tables':
            for we_need_this_table in options_dict['tables']:
                tables.add(we_need_this_table.lower())
            continue

        # FIXME!!!
        flag = False
        for item in only_type:
            if key.startswith(item):
                flag = True
        if flag:
            continue

        # FIXME!!!
        flag = True
        for item in {'filter', 'groupby', 'aggregate'}:
            if key.startswith(item):
                flag = False
        if flag:
            continue


        column_name = value[0].split(SPLIT_SYMBOL)[0]
        print(f'column_name : {column_name}')
        if column_name != 'inn' and column_name != 'upd_date':
            tables.add(ASK_DICT[column_name]['table_name'])
    print(f'we will use tables: {tables}')
    return tables


def get_joining_filter(options_dict:  Dict[str, List[str]]):
    tables = get_tables_set(options_dict)
    filter_and = []
    for table_pair in itertools.combinations(USED_TABLES, 2):
        name_pair = {table_pair[0].__name__, table_pair[1].__name__}
        if tables & name_pair == name_pair:
            filter_and.append(sqla.and_(
                table_pair[0].inn == table_pair[1].inn,
                table_pair[0].upd_date == table_pair[1].upd_date,
            ))
    return sqla.and_(*filter_and)


def make_filter(text_filter: Dict[str, Any]):
    value = text_filter['value']
    sign = text_filter['sign']
    column = text_filter['column_obj']
    if sign == 'gt':
        return column > value[0]
    if sign == 'gte':
        return column >= value[0]
    if sign == 'lt':
        return column < value[0]
    if sign == 'lte':
        return column <= value[0]
    if sign == 'eq':
        return column == value[0]
    if sign != 'range':
        raise Exception(f'undefined filter sign: {sign}')
    buf = []
    for case in value:
        if isinstance(case, tuple):
            buf.append(sqla.and_(case[0] <= column, column <= case[1]))
        else:
            buf.append(column == case)
    return sqla.and_(*buf)


def make_query(
        text_query: ParsedQuery,
        column_list: List[Dict[str, Any]],
        options_dict: Dict[str, List[str]]
):
    with session_scope() as session:
        query = session.query(*[item['column_obj'] for item in column_list])

        # for case we should join more then one table
        if len(get_tables_set(options_dict)) > 1:
            query = query.filter(get_joining_filter(options_dict))

        # just filters
        for text_filter in text_query[FILTER_KEY]:
            query = query.filter(make_filter(text_filter))

        # perform group by
        if len(text_query[GROUP_KEY]) > 0:
            query = query.group_by(*[grouper['column_obj'] for grouper in text_query[GROUP_KEY]])

        # FIXME limit for debugging
        # query = query.limit(50 * 100)
        return query.all()


def get_query(options_dict: Dict[str, List[str]]) -> Tuple[List[Any], List[str]]:
    text_query = extract_params(options_dict)
    print(f'text_query: {text_query}')

    tables = get_tables_set(options_dict)
    column_list = column_determiner(text_query, list(tables))

    return (
        make_query(text_query, column_list, options_dict),
        get_human_headers(column_list, text_query[AGGREGATE_KEY])
    )
