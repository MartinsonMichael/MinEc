from django.apps import AppConfig
from django.http import JsonResponse, HttpResponse
import json
from dbcontroller.models import Company
from django.core import serializers
from django.db.models import Q
from dbcontroller.models import create_ASK_DICT
import datetime
from django.db.models import Sum, Count, Avg


class ApiConfig(AppConfig):
    name = 'api'


ASK_DICT = None

def get_template_HTTP_RESPONSE():
    resp = HttpResponse()
    resp["Access-Control-Allow-Origin"] = '*'
    return resp


def get_ask_dict(request):
    global ASK_DICT
    if ASK_DICT is None:
        ASK_DICT = create_ASK_DICT()
    resp = get_template_HTTP_RESPONSE()
    resp.content = json.dumps({
        'ask_dict': ASK_DICT,
    })
    return resp


def parse_value(value, case):
    value = value[:-1]
    if case['type'] == 'multi':
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


def make_q_dict(prop, sign, value):
    if sign == 'range' and not isinstance(value, tuple):
        return {prop: value}
    if sign == 'eq':
        return {prop: value}
    return {'{0}__{1}'.format(prop, sign): value}


def process_single_filter(filter_str, q):
    filter_str = filter_str.split('___')
    prop = filter_str[0]
    sign = filter_str[1]
    value = filter_str[2:]
    value = parse_value(value, ASK_DICT[prop])
    print(value)
    if len(value) > 1:
        sign = 'range'
    or_array = []
    for num in value:
        or_array.append(Q(**make_q_dict(prop, sign, num)))
    print('or_array :', or_array)
    q_filter, or_array = or_array[0], or_array[1:]
    for item in or_array:
        q_filter = q_filter | item
    q = q.filter(q_filter)
    return q


def process_filters(options, q):
    for key, value in options.items():
        if key[:6] != 'filter':
            continue
        q = process_single_filter(value[0], q)
    return q


def process_groupby(options, q):
    values = []
    for key, value in options.items():
        if key[:6] == 'groupb':
            values.append(value[0])
    print('gb :', values)
    if len(values) > 0:
        q = q.values(*values)
    return q


def process_aggregations(options, q):
    for key, value in options.items():
        if key[:6] == 'groupb':
            return process_aggregations_groupped_case(options, q)
    return process_aggregations_not_groupped_case(options, q)


def process_aggregations_not_groupped_case(options, q):
    values = []
    for key, value in options.items():
        if key[:6] != 'aggreg':
            continue
        sign, value = value[0].split('___')
        values.append({
            'count': Count(value),
            'sum': Sum(value),
            'avg': Avg(value)
        }[sign])
    print('agg_ngc :', values)
    if len(values) > 0:
        q = [q.aggregate(*values)]
    return q


def process_aggregations_groupped_case(options, q):
    values = []
    for key, value in options.items():
        if key[:6] != 'aggreg':
            continue
        sign, value = value[0].split('___')
        values.append({
            'count': Count(value),
            'sum': Sum(value),
            'avg': Avg(value)
        }[sign])
    print('agg_gc :', values)
    if len(values) > 0:
        q = q.annotate(*values)
    return q


def process_options(options):
    q = Company.objects
    q = process_filters(options, q)
    q = process_groupby(options, q)
    q = process_aggregations(options, q)

    # q = Company.objects.values('location_code').annotate(Sum('taxbase__tax_atribute_1'))
    # print(q.count())

    return q


def create_value_list(options, q):
    if isinstance(q, list):
        return q
    if isinstance(q, dict):
        return [q]
    return list(q)


def create_human_headers(header):
    ans = []
    for x in header:
        f = False
        for name in ASK_DICT.keys():
            if name == x:
                ans.append(ASK_DICT[name]['human'])
                f = True
                break
        if f:
            continue
        ans.append('-')
        for name in ASK_DICT.keys():
            if x.startswith(name) and len(name) > len(ans[-1]):
                ans[-1] = ASK_DICT[name]['human']
        ATR = {
            'sum': 'Сумма',
            'count': 'Количество',
            'avg': 'Среднее'
        }
        for name in ATR.keys():
            if x.endswith(name):
                ans[-1] = ATR[name] + ' ' + ans[-1]
    return ans


def perform_api(request):
    global ASK_DICT
    if ASK_DICT is None:
        ASK_DICT = create_ASK_DICT()
    resp = get_template_HTTP_RESPONSE()
    options = dict(request.GET)
    print(options)

    table_err = []
    table_header = json.dumps(['None'])
    table_human_header = json.dumps(['None'])
    table_body = json.dumps([{'None': 1}])

    query = None
    try:
        query = process_options(options)
        query = create_value_list(options, query)

        if len(query) == 0:
            table_err.append('Zero query')

        if len(query) > 5 * 10**3:
            table_err.append('Too large query')

    except:
        table_err.append('Error while parsing')

    def my_ser(x):
        if isinstance(x, (datetime.datetime, datetime.date)):
            return str(x.day) + '.' + str(x.month) + '.' + str(x.year)

    if len(table_err) == 0:
        try:
            header = list(query[0].keys())
            table_header = json.dumps(header)
            table_human_header = json.dumps(create_human_headers(header))
            table_body = json.dumps(list(query), default=my_ser)
        except:
            table_err.append('Error while json dumping')

    print(query)
    print('err :', table_err)
    print('query len :', len(query) if query is not None else 'None')

    resp.content = json.dumps({
        'table_header': table_header,
        'table_human_header': table_human_header,
        'table_body': table_body,
        'table_error': json.dumps(table_err),
    })
    return resp
