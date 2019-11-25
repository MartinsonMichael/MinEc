import datetime
import json
import csv
import os
from typing import Tuple

from django.http import HttpResponse, StreamingHttpResponse
from django.utils.encoding import smart_str
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
    ticket = datetime.datetime.timestamp(datetime.datetime.now())
    options = dict(request.GET)

    query, human_header = get_query(options)

    if 'file' in options.keys():
        return send_as_file(query, human_header, ticket)

    return send_as_content(query, human_header, ticket)


def serializer(x):
    if isinstance(x, (datetime.datetime, datetime.date)):
        return str(x.day) + '.' + str(x.month) + '.' + str(x.year)
    if isinstance(x, Choice):
        return x.code


def stringifier(x):
    if isinstance(x, Choice):
        return str(x.code)
    return str(x)


def send_as_content(query, header, ticket):
    response = get_template_HTTP_RESPONSE()
    response.content = json.dumps({
        'table_human_header': json.dumps(header),
        'table_body': json.dumps(query, default=serializer),
    })
    return response


def write_as_csv_file(query, header, ticket) -> Tuple[str, str]:
    file_name = f'data_{ticket}.csv'
    file_path = os.path.join('home', 'michael', 'sent_files', file_name)
    with open(file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        for line in query:
            writer.writerow([stringifier(x) for x in line])
    return file_path, file_name


def send_as_file(query, header, ticket):
    file_path, file_name = write_as_csv_file(query, header, ticket)

    response = HttpResponse(content='application/force-download')  # mimetype is replaced by content_type for django 1.7
    response["Access-Control-Allow-Origin"] = '*'
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    response['X-Sendfile'] = smart_str(file_path)
    # It's usually a good idea to set the 'Content-Length' header too.
    # You can also set any other required headers: Cache-Control, etc.
    return response

    # response = StreamingHttpResponse(
    #     [
    #         ','.join(header) + '\n',
    #         *list(map(
    #             lambda line: ','.join([stringifier(item) for item in line]) + '\n',
    #             query
    #         ))
    #     ],
    #     content_type="text/csv"
    # )
    # response["Access-Control-Allow-Origin"] = '*'
    # response['Content-Disposition'] = f'attachment; filename=data.csv'
    #
    # return response
