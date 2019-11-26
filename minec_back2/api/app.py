import mimetypes
from datetime import datetime
import json
import csv
import os
import time
from typing import Tuple, Any, Optional
from multiprocessing import Process
from wsgiref.util import FileWrapper

from django.http import HttpResponse, StreamingHttpResponse
from django.utils.encoding import smart_str
from sqlalchemy_utils import Choice

from api.q_performing import get_query
from dbcontroller.model_support import create_AskDict
from dbcontroller.models import TicketTable
from dbcontroller.session_contoller import session_scope, sub_session_scope


FILE_STORAGE = os.path.join('/', 'home', 'michael', 'sent_files')


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

    ticket = get_ticket(ticket_id)
    response.content = json.dumps({
        'ticket_id': ticket['ticket_id'],
        'ticket_status': ticket['status'],
    })
    return response


def get_ticket(ticket_id):
    with sub_session_scope() as session:
        ticket = (
            session
                .query(
                     TicketTable.ticket_id,
                     TicketTable.status,
                     TicketTable.file_path,
                     TicketTable.query_options
                )
                .filter(TicketTable.ticket_id == ticket_id)
                .first()
        )

    ticket = {k: v for k, v in zip(['ticket_id', 'status', 'file_path', 'query_options'], ticket)}
    print(ticket)
    return ticket


def create_ticket(options: Any) -> str:
    ticket = str(int(time.mktime(datetime.now().timetuple())))
    with session_scope() as session:
        session.add(TicketTable(
            ticket_id=ticket,
            status='created',
            file_path='',
            query_options=json.dumps(options),
        ))
    return ticket


def try_to_update_ticket_status(*args, **kwargs):
    times = 0
    while True:
        try:
            set_ticket_status(*args, **kwargs)
            print('status was successfully updated')
            break
        except:
            print('status update failed')
            times += 1
            time.sleep(5)

        if times > 10:
            break


def set_ticket_status(
        ticket_id: str,
        status: Optional[str] = None,
        file_path: Optional[str] = None
):
    with session_scope() as session:
        ticket_obj = session.query(TicketTable).filter(TicketTable.ticket_id == ticket_id).first()

        if ticket_obj is None:
            raise ValueError('fuck this shit')

        if status is not None:
            ticket_obj.status = status
        if file_path is not None:
            ticket_obj.file_path = file_path


def perform_api(request):
    options = dict(request.GET)
    ticket_id = create_ticket(options)

    Process(target=__sub_perform_api, args=(request, ticket_id)).start()

    # __sub_perform_api(request, ticket_id)

    response = get_template_HTTP_RESPONSE()
    response.content = json.dumps({
        'ticket': ticket_id
    })
    return response


def __sub_perform_api(request, ticket: str):
    options = dict(request.GET)

    try_to_update_ticket_status(ticket, 'start perform query')

    try:
        query, human_header = get_query(options)
    except:
        try_to_update_ticket_status(ticket, 'error while performing query')
        return

    try_to_update_ticket_status(ticket, 'start write to file')
    try:
        write_as_csv_file(query, human_header, ticket)
    except:
        try_to_update_ticket_status(ticket, 'error while wring to file')
        return

    set_ticket_status(ticket, 'ready')


def serializer(x):
    if isinstance(x, datetime):
        return str(x.day) + '.' + str(x.month) + '.' + str(x.year)
    if isinstance(x, Choice):
        return x.code


def stringifier(x):
    if isinstance(x, Choice):
        return str(x.code)
    return str(x)


def write_as_csv_file(query, header, ticket_id):
    if not os.path.exists(FILE_STORAGE):
        os.makedirs(FILE_STORAGE)

    file_name = f'data_{ticket_id}.csv'
    file_path = os.path.join(FILE_STORAGE, file_name)
    with open(file_path, 'w+') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        for line in query:
            writer.writerow([stringifier(x) for x in line])
    try_to_update_ticket_status(ticket_id, file_path=file_path)


def get_ticket_content(request):
    ticket_id = dict(request.GET)['ticket_id'][0]
    ticket = get_ticket(ticket_id)
    if 'file' in json.loads(ticket['query_options']).keys():
        return send_as_file(ticket['file_path'])
    else:
        return send_as_content(ticket['file_path'])


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
