from django.http import HttpResponse
from dbcontroller.models import LoadDates
from django.db.models import Q
from dbcontroller.model_support import create_ASK_DICT, create_base_to_fields_dicts
import datetime
from django.db.models import Sum, Count, Avg


ASK_DICT = None
b2f, f2b = None, None


def parse_value(value, case):
    '''
    :return list of or values
    '''
    value = value[:-1]

    if case['type'] == 'bool':
        return [bool(value[0])]

    if case['type'] == 'multy':
        print(value)
        print(case)
        new_value = [case['machine_mapper'][int(x)] for x in value]
        print(new_value)
        return [case['machine_mapper'][int(x)] for x in value]

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
    global ASK_DICT, b2f, f2b
    if ASK_DICT is None or b2f is None or f2b is None:
        ASK_DICT = create_ASK_DICT()
        b2f, f2b = create_base_to_fields_dicts()
    q = LoadDates.objects
    q = process_filters(options, q)
    q = process_groupby(options, q)
    q = process_aggregations(options, q)

    return create_value_list(options, q)


def process_options_qs_file(options):
    global ASK_DICT, b2f, f2b
    if ASK_DICT is None or b2f is None or f2b is None:
        ASK_DICT = create_ASK_DICT()
        b2f, f2b = create_base_to_fields_dicts()
    q = LoadDates.objects
    q = process_filters(options, q)
    q = process_groupby(options, q)
    q = process_aggregations(options, q)
    return q


def ai_ordering(q):
    if len(q) == 0:
        return q
    sample = q[0]
    sort_key = []
    if 'date' in sample.keys():
        sort_key.append('date')
    for key in sample.keys():
        if key in ASK_DICT.keys():
            if ASK_DICT[key]['type'] == 'multy':
                sort_key.append(key)
    q.sort(key=lambda x: tuple(x[i] for i in sort_key))
    return q


def create_value_list(options, q):
    def make_list():
        if isinstance(q, list):
            return q
        if isinstance(q, dict):
            return [q]

        for key, value in options.items():
            if not key.startswith('filter'):
                print('HERE!')
                return list(q)

        fields = []
        tables = []
        for key, value in options.items():
            if key.startswith('filter'):
                tables.append(f2b[value[0].split('___')[0]])

        tables = list(set(tables) - set(['Company']))
        for table in ['Company'] + tables:
            fields.extend(b2f[table])

        print('fields we need : ', fields)
        return q.values(*fields)
        # return q.values()
    q = make_list()
    q = ai_ordering(q)
    return q


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


def create_human_headers_dict(header):
    ans = dict()
    for x in header:
        ans[x] = ''
        f = False
        for name in ASK_DICT.keys():
            if name == x:
                ans[x].append(ASK_DICT[name]['human'])
                f = True
                break
        if f:
            continue
        ans[x].append('-')
        for name in ASK_DICT.keys():
            if x.startswith(name) and len(name) > len(ans[x]):
                ans[x] = ASK_DICT[name]['human']
        ATR = {
            'sum': 'Сумма',
            'count': 'Количество',
            'avg': 'Среднее'
        }
        for name in ATR.keys():
            if x.endswith(name):
                ans[x] = ATR[name] + ' ' + ans[x]
    return ans


