import os

from celery import Celery

from dbcontroller.q_performing import try_to_update_ticket_status, get_query, FILE_STORAGE

app = Celery('tasks', broker='pyamqp://guest@rabbit//')


@app.task
def __sub_perform_api(options, ticket_id: str):
    try_to_update_ticket_status(ticket_id, 'start perform query')

    file_name = f'data_{ticket_id}.csv'
    file_path = os.path.join(FILE_STORAGE, file_name)

    try:
        get_query(options, ticket_id, file_path)
    except:
        try_to_update_ticket_status(ticket_id, 'error while performing query')
        return

    try_to_update_ticket_status(ticket_id, 'ready')


@app.task
def __remove_old_query():
    pass
