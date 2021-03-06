import mimetypes
from datetime import datetime
import json
import csv
import os
import time
from typing import Tuple, Any, Optional
from wsgiref.util import FileWrapper

from celery_app.apps import __sub_perform_api
from django.http import HttpResponse, StreamingHttpResponse

from dbcontroller.model_support import create_AskDict, serializer
from dbcontroller.q_performing import FILE_STORAGE


def get_template_HTTP_RESPONSE():
    resp = HttpResponse()
    resp["Access-Control-Allow-Origin"] = '*'
    return resp


def get_ask_dict(request):
    # with session_scope() as session:
    #     session.add(DateList(date=datetime.strptime('18.10.2019', '%d.%m.%Y')))

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


def get_ticket_status(request):
    response = get_template_HTTP_RESPONSE()
    ticket_id = dict(request.GET)['ticket_id'][0]

    print(f'ticket id : {ticket_id}')

    try:
        file_name = f'status_{ticket_id}.csv'
        file_path = os.path.join(FILE_STORAGE, file_name)
        with open(file_path, 'r') as file:
            status = file.readline()
    except:
        status = 'undefined'

    # ticket = get_ticket(ticket_id)
    response.content = json.dumps({
        'ticket_id': ticket_id,
        'ticket_status': status,
    })
    return response


def create_ticket(options: Any) -> str:
    ticket = str(int(time.mktime(datetime.now().timetuple())))
    return ticket


def delete_ticket_info(ticket_id: str):
    try:
        file_name = f'data_{ticket_id}.csv'
        file_path = os.path.join(FILE_STORAGE, file_name)
        os.remove(file_path)
    except:
        pass

    try:
        file_name = f'status_{ticket_id}.csv'
        file_path = os.path.join(FILE_STORAGE, file_name)
        os.remove(file_path)
    except:
        pass


def perform_api(request):
    options = dict(request.GET)
    ticket_id = create_ticket(options)

    __sub_perform_api.delay(dict(request.GET), ticket_id)

    response = get_template_HTTP_RESPONSE()
    response["Access-Control-Allow-Origin"] = '*'
    response.content = json.dumps({'ticket': ticket_id})
    return response


def get_ticket_content(request):
    ticket_id = dict(request.GET)['ticket_id'][0]
    is_file = int(dict(request.GET)['file'][0]) == 1
    # ticket = get_ticket(ticket_id)

    file_name = f'data_{ticket_id}.csv'
    file_path = os.path.join(FILE_STORAGE, file_name)

    if is_file:
        return send_as_file(file_path)
    else:
        return send_as_content(file_path)


def send_as_content(file_path):
    response = get_template_HTTP_RESPONSE()

    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        header = next(reader)
        query = []
        for line in reader:
            query.append(line)

    response.content = json.dumps({
        'table_human_header': json.dumps(header),
        'table_body': json.dumps(query, default=serializer),
    })
    return response


def send_as_file(file_path):
    file_name = os.path.basename(file_path)
    chunk_size = 8192
    response = StreamingHttpResponse(
        FileWrapper(open(file_path, 'rb'), chunk_size),
        content_type=mimetypes.guess_type(file_path)[0]
        # content_type="text/csv",
    )
    response['Content-Length'] = os.path.getsize(file_path)
    response['Content-Disposition'] = "attachment; filename=%s" % file_name
    response["Access-Control-Allow-Origin"] = '*'

    return response
