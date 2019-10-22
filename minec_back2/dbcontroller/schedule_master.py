import datetime
from bs4 import BeautifulSoup
import urllib.request
import requests
import zipfile
from typing import Dict, Any

from dbcontroller import parsers
import os
import signal
import time

from dbcontroller.parsers import parse_folder

BUFFER_DIR = './data/'
PAGE_TYPES = {
    'Company': {
        'name': 'Единый реестр субъектов малого и среднего предпринимательства',
        'url_name': '7707329152-rsmp',
        'folder_name': 'company',
        'parsers': parsers.parse_company,
    },
    'EmployeeNum': {
        'name': 'Сведения о среднесписочной численности работников организации',
        'url_name': '7707329152-sshr',
        'folder_name': 'employee_num',
        'parsers': parsers.parse_employee_num,
    },
    'BaseIncome': {
        'name': 'Сведения о суммах доходов и расходов по данным бухгалтерской'
                ' (финансовой) отчетности организации за год, предшествующий '
                'году размещения таких сведений на сайте ФНС России',
        'url_name': '7707329152-revexp',
        'folder_name': 'income',
        'parsers': parsers.parse_income,
    },
    'TaxBase': {
        'name': 'НАЛОГИ',
        'url_name': '7707329152-paytax',
        'folder_name': 'taxes',
        'parsers': parsers.parse_tex,
    },
    # OKVED: {
    #     'name': 'ОКВЕД',
    #     'url_name': '7707329152-rsmp',
    #     'parser': parsers.OkvedParser,
    #     'priority': 1,
    # }
}


def master_single(upd_date: datetime.date = None, steps: int = None):
    if not upd_date:
        upd_date = datetime.datetime.now().date()
    for base_name, description in PAGE_TYPES.items():
        _try_update_base(description, upd_date, steps)


def get_updated_base_list(force=False):
    upd = []
    for base in PAGE_TYPES.keys():
        if force or has_got_update(base):
            upd.append(base)
    return upd


def _try_update_base(
        description: Dict[str, Any],
        upd_date: datetime.date,
        steps: int = None,
        need_load=True,
        need_unzip=True,
        need_add=True,
):

    cur_upd_dir = os.path.join(BUFFER_DIR, str(upd_date))
    if not os.path.exists(cur_upd_dir):
        os.makedirs(cur_upd_dir)

    zip_file_name = os.path.join(cur_upd_dir, description['folder_name'] + '.zip')
    folder_name = os.path.join(cur_upd_dir, description['folder_name'])

    # load data
    if need_load:
        print(f"load {description['folder_name']}")
        _load_data(description['url_name'], zip_file_name)

    # unzip
    if need_unzip:
        print(f"unzip {description['folder_name']}")
        _extract_data(zip_file_name, folder_name)

    # add
    if need_add:
        print(f"add {description['folder_name']}")
        parse_folder(folder_name, upd_date, description['parsers'], steps=steps)


def has_got_update(base):
    page_type = PAGE_TYPES[base]
    data_name = "www.nalog.ru/opendata/" + page_type['url_name']
    html = requests.get("http://" + data_name).text
    soup = BeautifulSoup(html, 'html.parser')

    date_text = str(soup.find(text="Дата актуальности").parent.parent)
    return datetime.datetime.now().date() > datetime.datetime.strptime(
        BeautifulSoup(date_text, 'html.parser').find('tr').findAll('td')[-1].text, '%d.%m.%Y').date()


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
