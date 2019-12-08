import time, os, stat
from celery import Celery
from celery.schedules import crontab

from dbcontroller.q_performing import try_to_update_ticket_status, get_query, FILE_STORAGE
from dbcontroller.schedule_master import any_has_updates, master_single

app = Celery('tasks', broker='pyamqp://guest@rabbit//')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    sender.add_periodic_task(crontab(minute=0, hour='*/3'), __remove_old_query.s(), name='old query remover')

    sender.add_periodic_task(crontab(minute=0, hour=3, day_of_week='sunday'), __updater.s(), name='update database')



@app.task
def test(arg):
    print(arg)


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


def file_age_in_seconds(pathname):
    return time.time() - os.stat(pathname)[stat.ST_MTIME]


@app.task
def __remove_old_query():
    for file_name in os.listdir(FILE_STORAGE):
        file_path = os.path.join(FILE_STORAGE, file_name)
        if file_age_in_seconds(file_path) > 1 * 60 * 60:
            os.remove(file_path)


@app.task()
def __updater():
    if not any_has_updates():
        print('no any updates')
        return
    master_single()
