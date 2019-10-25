import datetime
import json
from django.http import HttpResponse, StreamingHttpResponse
from sqlalchemy_utils import Choice

from api.q_performing import get_query
from dbcontroller.model_support import create_AskDict



def get_template_HTTP_RESPONSE():
    resp = HttpResponse()
    resp["Access-Control-Allow-Origin"] = '*'
    return resp


def get_ask_dict(request):

    # with session_scope() as session:
    #     session.add(DateList(date=datetime.datetime.strptime('18.10.2019', '%d.%m.%Y')))

    resp = get_template_HTTP_RESPONSE()
    askDict = create_AskDict()
    real_to_send = {}
    for key, info in askDict.items():
        if key.startswith('inn') and key != 'inn':
            continue
        if key.startswith('upd_date') and key != 'upd_date':
            continue
        real_to_send[key] = info
    resp.content = json.dumps({
        'ask_dict': real_to_send,
    }, default=serializer)
    return resp


def perform_api(request):
    options = dict(request.GET)

    query, human_header = get_query(options)

    if 'file' in options.keys():
        return send_as_file(query, human_header)

    return send_as_content(query, human_header)


def serializer(x):
    if isinstance(x, (datetime.datetime, datetime.date)):
        return str(x.day) + '.' + str(x.month) + '.' + str(x.year)
    if isinstance(x, Choice):
        return x.code


def stringifier(x):
    if isinstance(x, Choice):
        return str(x.code)
    return str(x)


def send_as_content(query, header):
    response = get_template_HTTP_RESPONSE()
    response.content = json.dumps({
        'table_human_header': json.dumps(header),
        'table_body': json.dumps(query, default=serializer),
    })
    return response


def send_as_file(query, header):

    response = StreamingHttpResponse(
        [
            ','.join(header) + '\n',
            *list(map(
                lambda line: ','.join([stringifier(item) for item in line]) + '\n',
                query
            ))
        ],
        content_type="text/csv"
    )
    response["Access-Control-Allow-Origin"] = '*'
    response['Content-Disposition'] = f'attachment; filename=data.csv'

    return response
