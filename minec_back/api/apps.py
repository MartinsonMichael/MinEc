from django.apps import AppConfig
from django.http import HttpResponse, StreamingHttpResponse, FileResponse
import json
import datetime
from .qs_peroforming import create_human_headers, process_options, process_options_qs_file, create_human_headers_dict
from djqscsv import write_csv
from enum import Enum, unique
from django.utils.encoding import smart_str
import os

@unique
class Errors(Enum):
    parse = 0
    zero = 1
    too_large = 2
    json_dump = 3

    def __str__(self):
        if self == Errors.parse:
            return "ошибка просессинга запроса; "
        if self == Errors.zero:
            return "ноль записей в результате; "
        if self == Errors.too_large:
            return "слишком много записей, показаны первые 10, " \
                   "для загрузки всего выбирите опцию 'загрузка файла'; "
        if self == Errors.json_dump:
            return "ошибка json dump'ирования; "
        return "неизвестная ошибка; "


class ApiConfig(AppConfig):
    name = 'api'

def get_template_HTTP_RESPONSE():
    resp = HttpResponse()
    resp["Access-Control-Allow-Origin"] = '*'
    return resp


def perform_api(request):
    resp = get_template_HTTP_RESPONSE()
    options = dict(request.GET)
    #options = {k.replace('|||', ' '): [v[0].replace('|||', ' ')] for k, v in options}
    print(options)

    table_err = []
    table_header = json.dumps(['None'])
    table_human_header = json.dumps(['None'])
    table_body = json.dumps([{'None': 1}])

    query = None
    try:
        query = process_options(options)

        if len(query) == 0:
            table_err.append(Errors.zero)

        if len(query) > 5 * 10**3:
            table_err.append(Errors.too_large)

    except:
        table_err.append(Errors.parse)

    def my_ser(x):
        if isinstance(x, (datetime.datetime, datetime.date)):
            return str(x.day) + '.' + str(x.month) + '.' + str(x.year)

    if Errors.too_large in table_err:
        query = query[:10]

    wasUpdGr = False
    for key, value in options.items():
        if key[:6] == 'groupb':
            if value[0] == 'upd_date':
                wasUpdGr = True

    if wasUpdGr:
        try:
            header = list(query[0].keys()) + ['upd_date']
            table_header = json.dumps(header)
            table_human_header = json.dumps(create_human_headers(header))
            query = list(query)
            print(query)
            query = [{**x, **{'upd_date': '19.06.2019'}} for x in query]
            print(query)
            table_body = json.dumps(query, default=my_ser)
        except:
            table_err.append(Errors.json_dump)
    else:
        try:
            header = list(query[0].keys())
            table_header = json.dumps(header)
            table_human_header = json.dumps(create_human_headers(header))
            table_body = json.dumps(list(query), default=my_ser)
        except:
            table_err.append(Errors.json_dump)

    table_err = [str(x) for x in table_err]
    # print(query[:4])
    print('err :', table_err)
    print('query len :', len(query) if query is not None else 'None')

    resp.content = json.dumps({
        'table_header': table_header,
        'table_human_header': table_human_header,
        'table_body': table_body,
        'table_error': json.dumps(table_err),
    })
    return resp


def sent_q_as_file(request):
    options = dict(request.GET)
    query = process_options_qs_file(options)
    file_name = "file_" + str(datetime.datetime.now()).replace(' ', '_') + ".csv"

    header = list(query[0].keys())
    write_csv(query, open(file_name, 'wb'), field_header_map=create_human_headers_dict(header))

    print(f'save {file_name}')

    # response = FileResponse(open(file_name))
    # response["Access-Control-Allow-Origin"] = '*'

    response = StreamingHttpResponse(open(file_name, 'rb').readlines(), content_type="text/csv")
    response["Access-Control-Allow-Origin"] = '*'
    response['Content-Disposition'] = f'attachment; filename={smart_str(file_name)}'

    return response


def download_table_by_date(request):
    from dbcontroller.models import Company, TaxBase, BaseIncome, EmployeeNum, Alive, OKVED, LoadDates
    from dbcontroller.model_support import create_ASK_DICT

    ASK_DICT = create_ASK_DICT()

    options = dict(request.GET)
    print(options)

    table_name = options['table'][0]
    table_date = datetime.datetime.strptime(options['date'][0], '%d.%m.%Y')

    file_name = "file_" + str(datetime.datetime.now()).replace(' ', '_') + ".csv"
    print(f'table_date : {table_date}, table_name : {table_name}')
    loadDateObj = LoadDates.objects.get(date=table_date)
    print(loadDateObj)

    query = None
    if table_name == 'Company':
        query = Company
    if table_name == 'TaxBase':
        query = TaxBase
    if table_name == 'BaseIncome':
        query = BaseIncome
    if table_name == 'EmployeeNum':
        query = EmployeeNum
    if table_name == 'Alive':
        query = Alive
    if table_name == 'OKVED':
        query = OKVED

    query = query.objects
    query = query.filter(upd_date=loadDateObj)

    field = []

    bufheader = list(set(query.values()[0].keys()) - {'id', '_inn_id'})

    bufbufheader = bufheader + ['_inn__inn']

    query = query.values(*bufbufheader)

    print(f'bufheaders : {bufheader}')

    header = list(query[0].keys())

    name_dict = {'_inn__inn': 'ИНН'}

    for key, value in ASK_DICT.items():
        val2 = '__'.join(key.split('__')[1:])
        if val2 in bufheader:
            print(f'find {key}')
            name_dict[val2] = value['human']


    write_csv(query, open(file_name, 'wb'), field_header_map=name_dict)

    response = StreamingHttpResponse(open(file_name, 'rb').readlines(), content_type="text/csv")
    response["Access-Control-Allow-Origin"] = '*'
    response['Content-Disposition'] = f'attachment; filename={smart_str(file_name)}'

    return response
