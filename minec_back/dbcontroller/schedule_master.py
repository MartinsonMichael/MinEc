from .models import ScheduleTable
import datetime
from bs4 import BeautifulSoup
import urllib.request
import requests
import os
import zipfile
from .models import Company, EmployeeNum, BaseIncome, TaxBase, OKVED, LoadDates

from dbcontroller import parsers

BUFFER_DIR = './buffer/'
PAGE_TYPES ={
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


def master(steps=None):
    page_types = sorted(list(PAGE_TYPES.keys()), key=lambda x: PAGE_TYPES[x]['priority'], reverse=True)
    upd_date = datetime.datetime.now().date()

    if LoadDates.objects.filter(date=upd_date).count() == 0:
        LoadDates(date=upd_date).save()

    for base in page_types:
        tries = 0
        while not _try_update_base(base, steps=steps, upd_date=upd_date):
            tries += 1
            if tries > 10:
                break


def _try_update_base(base, steps=None, upd_date=None):
    if upd_date is None:
        upd_date = datetime.datetime.now().date()
    q = ScheduleTable.objects.\
        filter(date__gte=datetime.datetime.now().date() - datetime.timedelta(days=14))

    base_name = base.__name__
    page_type = PAGE_TYPES[base]
    zip_file_name = os.path.join(BUFFER_DIR, page_type['url_name'] + '_data_zip.zip')
    folder_name = os.path.join(BUFFER_DIR, page_type['url_name'] + '_data_folder')

    # load data
    if q.filter(type='load').filter(zip_file_name=page_type['url_name']).count() == 0:
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
