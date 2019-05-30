from django.apps import AppConfig
from django.http import HttpResponse, StreamingHttpResponse
import json
import datetime
from .qs_peroforming import create_human_headers, process_options
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

    try:
        header = list(query[0].keys())
        table_header = json.dumps(header)
        table_human_header = json.dumps(create_human_headers(header))
        table_body = json.dumps(list(query), default=my_ser)
    except:
        table_err.append(Errors.json_dump)

    table_err = [str(x) for x in table_err]
    print(query[:4])
    print('err :', table_err)
    print('query len :', len(query) if query is not None else 'None')

    resp.content = json.dumps({
        'table_header': table_header,
        'table_human_header': table_human_header,
        'table_body': table_body,
        'table_error': json.dumps(table_err),
    })
    return resp


import csv

def sent_q_as_file(request):
    options = dict(request.GET)
    query = process_options(options)
    file_name = "file_" + str(datetime.datetime.now()).replace(' ', '_') + ".csv"

    write_csv(query, open(file_name, 'wb'))

    print(f'save {file_name}')

    response = StreamingHttpResponse(open(file_name, 'rb').readlines(), content_type="text/csv")
    response["Access-Control-Allow-Origin"] = '*'
    response['Content-Disposition'] = f'attachment; filename={smart_str(file_name)}'

    return response