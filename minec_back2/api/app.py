import datetime
import json
from django.http import HttpResponse
from sqlalchemy_utils import Choice

from api.q_performing import get_query
from dbcontroller.model_support import create_AskDict


def get_template_HTTP_RESPONSE():
    resp = HttpResponse()
    resp["Access-Control-Allow-Origin"] = '*'
    return resp


def get_ask_dict(request):
    resp = get_template_HTTP_RESPONSE()
    askDict = create_AskDict()
    real_to_send = {}
    for key, info in askDict.keys():
        if key.startswith('inn') and key != 'inn':
            continue
        if key.startswith('upd_date') and key != 'upd_date':
            continue
        real_to_send[key] = info
    resp.content = json.dumps({
        'ask_dict': real_to_send,
    })
    return resp


def perform_api(request):
    http_response = get_template_HTTP_RESPONSE()
    options = dict(request.GET)

    print(f'options: {options}')

    query, human_header = get_query(options)

    print(f'query len: {len(query)}')

    def my_serrializer(x):
        if isinstance(x, (datetime.datetime, datetime.date)):
            return str(x.day) + '.' + str(x.month) + '.' + str(x.year)
        if isinstance(x, Choice):
            return x.code

    http_response.content = json.dumps({
        'table_human_header': json.dumps(human_header),
        'table_body': json.dumps(query, default=my_serrializer),
    })
    return http_response
