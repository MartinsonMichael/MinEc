from .models import ScheduleTable
import datetime
from bs4 import BeautifulSoup
import urllib.request
import requests
import zipfile
from .models import Company, EmployeeNum, BaseIncome, TaxBase, OKVED, LoadDates
from .models import ThreadStore

from dbcontroller import parsers
import threading
import os
import signal
import time

BUFFER_DIR = './buffer/'
PAGE_TYPES = {
    Company: {
        'name': 'Единый реестр субъектов малого и среднего предпринимательства',
        'url_name': '7707329152-rsmp',
        'parser': parsers.CompanyMainParser,
        'priority': 10,
    },
    EmployeeNum: {
        'name': 'Сведения о среднесписочной численности работников организации',
        'url_name': '7707329152-sshr',
        'parser': parsers.EmployeesNumParser,
        'priority': 1,
    },
    BaseIncome: {
        'name': 'Сведения о суммах доходов и расходов по данным бухгалтерской'
                ' (финансовой) отчетности организации за год, предшествующий '
                'году размещения таких сведений на сайте ФНС России',
        'url_name': '7707329152-revexp',
        'parser': parsers.IncomeParser,
        'priority': 1,
    },
    TaxBase: {
        'name': 'НАЛОГИ',
        'url_name': '7707329152-paytax',
        'parser': parsers.TaxParser,
        'priority': 1,
    },
    OKVED: {
        'name': 'ОКВЕД',
        'url_name': '7707329152-rsmp',
        'parser': parsers.OkvedParser,
        'priority': 1,
    }
}


def launch_main_cycle():
    if ThreadStore.objects.filter(th_type='extra').count() > 0:
        main_pid = ThreadStore.objects.filter(th_type='main')[0].values
        os.kill(main_pid, signal.SIGTERM)

    threading.enumerate()


def relaunch_main():
    if ThreadStore.objects.filter(th_type='main').count() > 0:
        main_pid = ThreadStore.objects.filter(th_type='main').values('th_pid')
        for pid in main_pid:
            os.kill(pid, signal.SIGTERM)
    threading.Thread(
        group=None,
        target=__main_loop,
        daemon=False,
    ).start()


def __main_loop():
    ThreadStore(th_type='main', th_pid=threading.current_thread().ident).save()
    while True:
        master()
        time.sleep(60 * 60 * 24 * 1)


def master(steps=None, force=False, times=2):
    upd_date_date = datetime.datetime.now().date()
    if LoadDates.objects.filter(date=upd_date_date).count() == 0:
        date_item = LoadDates(date=upd_date_date)
        date_item.save()
    else:
        date_item = LoadDates.objects.order_by('-date')[0]
    if LoadDates.objects.count() >= 2:
        date_pre_last = LoadDates.objects.order_by('-date')[1]
    else:
        force = True
        date_pre_last = LoadDates.objects.order_by('-date')[0]

    to_upd = get_updated_base_list(force)
    not_today = [x for x in PAGE_TYPES.keys() if x not in to_upd]

    if len(to_upd) == 0:
        return

    if Company in to_upd:
        to_upd.remove(Company)
        for _ in range(times):
            _try_update_base(Company, steps=steps, upd_date=date_item)

    for _ in range(times):
        for base in to_upd:
            _try_update_base(base, steps=steps, upd_date=date_item)

    for base in not_today:
        q = base.objects.filter(upd_date=date_pre_last)
        if q.count() > 0:
            q.upd_date.add(date_item)


def get_updated_base_list(force=False):
    upd = []
    for base in PAGE_TYPES.keys():
        if force or has_got_update(base):
            upd.append(base)
    return upd


def _try_update_base(base, steps=None, upd_date=None):
    if upd_date is None:
        upd_date = datetime.datetime.now().date()
    q = ScheduleTable.objects.\
        filter(date__gte=datetime.datetime.now().date() - datetime.timedelta(days=14))

    base_name = base.__name__
    page_type = PAGE_TYPES[base]
    zip_file_name = os.path.join(BUFFER_DIR, page_type['url_name'] + '_data_zip.zip')
    folder_name = os.path.join(BUFFER_DIR, page_type['url_name'] + '_data_folder')

    if q.filter(type='done').filter(base_name=base_name).count() > 0:
        return True

    # load data
    if q.filter(type='load').filter(zip_file_name=page_type['url_name']).count() == 0:
        print('load')
        if _load_data(page_type['url_name'], zip_file_name):
            schedule_item = ScheduleTable(
                date=datetime.datetime.now().date(),
                type='load',
                zip_file_name=page_type['url_name'],
            )
            schedule_item.save()
        else:
            return False

    # unzip
    if q.filter(type='unzip').filter(zip_file_name=page_type['url_name']).count() == 0:
        print('unzip')
        if _extract_data(zip_file_name, folder_name):
            schedule_item = ScheduleTable(
                date=datetime.datetime.now().date(),
                type='unzip',
                zip_file_name=page_type['url_name'],
            )
            schedule_item.save()
            schedule_item = ScheduleTable(
                date=datetime.datetime.now().date(),
                type='need_to_add',
                zip_file_name=page_type['url_name'],
                file_name=str(len(os.listdir(folder_name))),
            )
            schedule_item.save()
        else:
            return False

    print('start adding')
    q = q.filter(base_name=base_name)

    # add
    if q.filter(type='add').count() != len(os.listdir(folder_name)):
        parser = page_type['parser'](steps=steps, upd_date=upd_date)
        if parser.parse_folder(folder_name) and steps is None:
            schedule_item = ScheduleTable(
                date=datetime.datetime.now().date(),
                type='done',
                base_name=base_name,
            )
            schedule_item.save()

    return q.filter(type='done').count() > 0


def has_got_update(base):
    page_type = PAGE_TYPES[base]
    data_name = "www.nalog.ru/opendata/" + page_type['url_name']
    html = requests.get("http://" + data_name).text
    soup = BeautifulSoup(html, 'html.parser')

    date_text = str(soup.find(text="Дата актуальности").parent.parent)
    return datetime.datetime.now().date() > datetime.datetime.strptime(
        BeautifulSoup(date_text, 'html.parser').find('tr').findAll('td')[-1].text, '%d.%m.%Y')


def _load_data(url_name, filename):
    try:
        data_name = "www.nalog.ru/opendata/" + url_name
        html = requests.get("http://" + data_name).text
        soup = BeautifulSoup(html, 'html.parser')

        part_with_data_link = str(soup.find(text="Гиперссылка (URL) на набор").parent.parent)
        data_link = BeautifulSoup(part_with_data_link, 'html.parser').find('a').get('href')

        if filename is None:
            filename = url_name + '_data_folder'
        file = open(filename, 'wb', 0o777)
        data = urllib.request.urlopen(data_link)
        for line in data:
            file.write(line)
        return True
    except:
        return False


def _extract_data(filename, dirname):
    try:

        if not os.path.exists(dirname):
            os.makedirs(dirname)
        zip_ref = zipfile.ZipFile(filename, 'r')
        zip_ref.extractall(dirname)
        zip_ref.close()
        return True
    except:
        return False
