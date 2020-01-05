import bs4
import os
from datetime import date
from typing import Callable
from multiprocessing import Pool
from functools import partial

from dbcontroller.session_contoller import session_scope

MAX_SIZE_TO_CREATE = 1 * 10 ** 3


def parse_folder(folder_name: str, upd_date: date, parser_func: Callable, thead_num: int = 4, steps: int = None):
    file_list_process_worker(
        os.listdir(folder_name) if steps is None else os.listdir(folder_name)[:steps],
        folder_name,
        upd_date,
        parser_func,
    )
    # pool = Pool(thead_num)
    # worker = partial(
    #     file_list_process_worker,
    #     folder_name=folder_name,
    #     upd_date=upd_date,
    #     parser_func=parser_func
    # )
    # pool.map(
    #     worker,
    #     os.listdir(folder_name) if steps is None else os.listdir(folder_name)[:steps],
    # )


def file_list_process_worker(files_list, folder_name, upd_date, parser_func):
    list_to_create = []
    for file in files_list:
        try:
            processed_items = [
                parser_func(item, inn, upd_date)
                for item, inn in iterate_over_file(os.path.join(folder_name, file))
            ]
            list_to_create.extend(processed_items)
        except:
            print('item parse failed')
        if len(list_to_create) > MAX_SIZE_TO_CREATE:
            save_list(list_to_create)
            list_to_create = []
    if len(list_to_create) > 0:
        save_list(list_to_create)


def save_list(list_to_create):
    try:
        with session_scope() as session:
            session.add_all(list_to_create)
    except:
        print(f'exception on insert :(')


def iterate_over_file(filename):
    print(f'start parse xml {filename}')
    soup = bs4.BeautifulSoup(open(filename, 'r').read(), 'xml')
    for item in soup.find_all('Документ'):
        inn = get_inn(item)
        if inn is not None:
            yield (item, inn)


def get_inn(item):
    try:
        inn = item.find('ИПВклМСП')['ИННФЛ']
        if inn is not None:
            return inn
    except:
        pass
    try:
        inn = item.find('ОргВклМСП')['ИННЮЛ']
        if inn is not None:
            return inn
    except:
        pass
    try:
        inn = item.find('СведНП')['ИННЮЛ']
        if inn is not None:
            return inn
    except:
        pass
    try:
        main_part = item.find('СведНП')

        if main_part.has_attr('ИННФЛ'):
            inn = main_part['ИННФЛ']
            return inn

        if main_part.has_attr('ИННЮЛ'):
            inn = main_part['ИННЮЛ']
            return inn
    except:
        pass

    print('No inn', item.pretitfy(), sep='\n', end='\n')
    return None
