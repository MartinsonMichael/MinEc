from django.apps import AppConfig
from django.http import JsonResponse, HttpResponse
import json
from dbcontroller.models import Company
from django.core import serializers

class ApiConfig(AppConfig):
    name = 'api'


def get_template_HTTP_RESPONSE():
    resp = HttpResponse()
    resp["Access-Control-Allow-Origin"] = '*'
    return resp


def get_ask_dict(request):

    # DEBUG
    #if ASK_DICT is None:
    from dbcontroller.models import fill_ASK_DICT
    fill_ASK_DICT()
    from dbcontroller.models import ASK_DICT

    resp = get_template_HTTP_RESPONSE()
    resp.content = json.dumps({
        'ask_dict': ASK_DICT,
    })
    return resp


def process_filters(options, q):
    for key, value in options.items():
        if key[:6] != 'filter':
            continue
        prop, sign, value = value[0].split('__')
        params = {'{0}__{1}'.format(prop, sign) : value}
        if sign == 'eq':
            params = {prop : value}
        q = q.filter(**params)
    return q


def process_options(options):
    q = Company.objects
    q = process_filters(options, q)
    return q


def perform_api(request):
    resp = get_template_HTTP_RESPONSE()
    options = dict(request.GET)
    print(options)

    query = process_options(options)
    db_json = serializers.serialize('json', query)

    headers_without_pk = list(json.loads(db_json)[0]['fields'].keys())

    headers_with_pk = list(query.values()[0].keys())

    resp.content = json.dumps({
        'table_header': list(headers_without_pk),
        'table_body': db_json,
        'table_pk': list(set(headers_with_pk) - set(headers_without_pk))[0],
    })

    return resp
