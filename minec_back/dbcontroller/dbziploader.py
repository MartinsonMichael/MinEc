import os
from bs4 import BeautifulSoup
import urllib.request
import requests
import zipfile
import maya
import traceback
from dbcontroller.models import Company, Alive, OKVED, TaxBase, Company, EmployeeNum, BaseIncome
from datetime import datetime
from django.db.models.functions import Extract
from django.db import transaction
import threading
import time
from django.core.cache import cache

BUFFER_DIR = './buffer/'
ASK_DICT = None
TAX_DICT = None
from dbcontroller.models import REGION_TYPES


def loadNewData(name, filename=None):
    print('load data...')
    dataname = "www.nalog.ru/opendata/" + name
    html = requests.get("http://" + dataname).text
    soup = BeautifulSoup(html, 'html.parser')
    partwithdatalink = str(soup.find(text="Гиперссылка (URL) на набор").parent.parent)
    datalink = BeautifulSoup(partwithdatalink, 'html.parser').find('a').get('href')

    if filename is None:
        filename = name + '_data_folder'
    file = open(filename, 'wb', 0o777)
    data = urllib.request.urlopen(datalink)
    for line in data:
        file.write(line)


def extractToDir(filename, dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname, 777)
    zip_ref = zipfile.ZipFile(filename, 'r')
    zip_ref.extractall(dirname)
    zip_ref.close()


def parseCompany(filename):
    print(f'start parse xml company {filename}')
    now_time = time.time()
    soup = BeautifulSoup(open(filename, 'r').read(), 'xml')
    to_create = {
        'company': [],
        'alive': [],
        'okved': []
    }
    for item in soup.find_all('Документ'):
        try:

            if item.find('ИПВклМСП') is not None:
                main_part = item.find('ИПВклМСП')
                inn = main_part['ИННФЛ']
                is_ip = True
                owner_name = " ".join(main_part.find('ФИОИП').attrs.values())
                short_title = None

            if item.find('ОргВклМСП') is not None:
                main_part = item.find('ОргВклМСП')
                inn = main_part['ИННЮЛ']
                is_ip = False
                owner_name = None
                if main_part.has_attr('НаимОргСокр'):
                    short_title = main_part['НаимОргСокр']
                elif main_part.has_attr('НаимОрг'):
                    short_title = main_part['НаимОрг']
                else:
                    short_title = None

            #cache.set(key=inn, value="upd", nx=True)

            if Company.objects.filter(inn=inn).count() > 0:
                continue

            location_code = int(item.find('СведМН')['КодРегион'])
            company = Company(
                inn=inn,
                owner_name=owner_name,
                short_title=short_title,
                is_ip=is_ip,
                location_code=location_code,
                region_name=REGION_TYPES[location_code],
            )
            to_create['company'].append(company)
            company.save()

            alive = Alive(
                _company=company,
                date_add_to_base=datetime.now().date(),
                # не совсем корректно, нужно найти подходящу базу
                date_create=maya.parse(item['ДатаВклМСП']).datetime(),
                date_disappear=None,
                still_alive=True,
                still_not_found=False,
                life_duration_years=0,
            )
            to_create['alive'].append(alive)
            to_create['okved'].extend(_add_okved(company, item))

            company.save()
            alive.save()


        except:
            print('Error while parsing:')
            print(item.prettify())
            print('\n***\nEroor:\n')
            traceback.print_exc()
            print('\n***\n')
            break

    for x in ['company', 'alive', 'okved']:
        print(f'in {x} {len(to_create[x])} items')

    #Company.objects.bulk_create(to_create['company'])
    #Alive.objects.bulk_create(to_create['alive'])
    #OKVED.objects.bulk_create(to_create['okved'])
    print(f'it took {(time.time() - now_time)}')


def _add_okved(company, item):
    buf = []
    # prime
    for okved in item.find('СвОКВЭД').findAll('СвОКВЭДОсн'):
        buf.append(OKVED(
            _company=company,
            code=okved['КодОКВЭД'],
            code_name=okved['НаимОКВЭД'],
            is_prime=True,
        ))
    # extra
    for okved in item.find('СвОКВЭД').findAll('СвОКВЭДДоп'):
        buf.append(OKVED(
            _company=company,
            code=okved['КодОКВЭД'],
            code_name=okved['НаимОКВЭД'],
            is_prime=True,
        ))
    return buf


def parseNumEmployees(filename):
    print(f'start parse xml employee numbers {filename}')
    soup = BeautifulSoup(open(filename, 'r').read(), 'xml')

    cnt = 0
    pss = 0
    with transaction.atomic():
        for item in soup.find_all('Документ'):
            cnt += 1
            try:
                inn = item.find('СведНП')['ИННЮЛ']
                employee_num = int(item.find('СведССЧР')['КолРаб'])

                employee_num_obj = None
                if EmployeeNum.objects.filter(inn=inn).count() == 0:
                    company = Company.objects.get(inn=inn)
                    employee_num_obj = EmployeeNum(
                        inn=company,
                    )
                else:
                    employee_num_obj = EmployeeNum.objects.get(inn=inn)
                employee_num_obj.employee_num = employee_num
                employee_num_obj.save()

            except Company.DoesNotExist:
                pss += 1
            except:
                print('Error while parsing:')
                print(item.prettify())
                print('\n***\nEroor:\n')
                traceback.print_exc()
                print('\n***\n')
                break

    print(f'pass rate : {pss} / {cnt}')


def parseTax(filename):
    print(f'start parse xml tex {filename}')
    soup = BeautifulSoup(open(filename, 'r').read(), 'xml')

    pss = 0
    cnt = 0
    with transaction.atomic():
        for item in soup.find_all('Документ'):
            try:
                cnt += 1
                main_part = item.find('СведНП')

                inn = None

                if main_part.has_attr('ИННФЛ'):
                    inn = main_part['ИННФЛ']

                if main_part.has_attr('ИННЮЛ'):
                    inn = main_part['ИННЮЛ']

                if inn is None:
                    continue


                tax_item = None
                if TaxBase.objects.filter(inn=inn).count() == 0:
                    company = Company.objects.get(pk=inn)

                    tax_item = TaxBase(
                        inn=company,
                    )
                else:
                    tax_item = TaxBase.objects.get(inn=inn)

                for tax in item.find_all('СвУплСумНал'):
                    setattr(tax_item, TAX_DICT[tax['НаимНалог']], tax['СумУплНал'])

                #buffer.append(tax_item)
                tax_item.save()

            except Company.DoesNotExist:
                pss += 1
            except:
                print('Error while parsing:')
                print(item.prettify())
                print('\n***\nEroor:\n')
                traceback.print_exc()
                print('\n***\n')
                break
    # TaxBase.objects.bulk_create(buffer)
    print(f'pass rate : {pss} / {cnt}')


def parseBuhUschet(filename):
    print(f'start parse xml income {filename}')
    soup = BeautifulSoup(open(filename, 'r').read(), 'xml')

    pss = 0
    cnt = 0
    with transaction.atomic():
        for item in soup.find_all('Документ'):
            try:
                cnt += 1
                main_part = item.find('СведНП')

                inn = None

                if main_part.has_attr('ИННФЛ'):
                    inn = main_part['ИННФЛ']

                if main_part.has_attr('ИННЮЛ'):
                    inn = main_part['ИННЮЛ']

                if inn is None:
                    continue

                income_item = None
                if BaseIncome.objects.filter(inn=inn).count() == 0:
                    company = Company.objects.get(pk=inn)
                    income_item = BaseIncome(
                        inn=company,
                    )
                else:
                    income_item = BaseIncome.objects.get(inn=inn)

                item = item.find('СведДохРасх')
                income_item.income = item['СумДоход']
                income_item.outcome = item['СумРасход']

                income_item.save()

            except Company.DoesNotExist:
                pss += 1
            except:
                print('Error while parsing:')
                print(item.prettify())
                print('\n***\nEroor:\n')
                traceback.print_exc()
                print('\n***\n')
                break
    print(f'pass rate : {pss} / {cnt}')


PAGE_TYPES = [
    {
        'name': 'Единый реестр субъектов малого и среднего предпринимательства',
        'url_name': '7707329152-rsmp',
        'parse_func': parseCompany
    },
    {
        'name': 'Сведения о среднесписочной численности работников организации',
        'url_name': '7707329152-sshr',
        'parse_func': parseNumEmployees,

    },
    {
        'name': 'Сведения о суммах доходов и расходов по данным бухгалтерской'
                ' (финансовой) отчетности организации за год, предшествующий '
                'году размещения таких сведений на сайте ФНС России',
        'url_name': '7707329152-revexp',
        'parse_func': parseBuhUschet,
    },
    {
        'name': 'НАЛОГИ',
        'url_name': '7707329152-paytax',
        'parse_func': parseTax,
    },
]


def addToDB(page_type, steps=None, skip_steps=None, need_load=None, need_unzip=None):
    global ASK_DICT, TAX_DICT
    if ASK_DICT is None:
        from dbcontroller.model_support import create_ASK_DICT
        ASK_DICT = create_ASK_DICT()
    if TAX_DICT is None:
        from dbcontroller.model_support import create_TAX_DICT
        TAX_DICT = create_TAX_DICT()

    print('start updating', page_type['name'])
    if not os.path.exists(BUFFER_DIR):
        os.makedirs(BUFFER_DIR, 777)

    dirname = os.path.join(BUFFER_DIR, page_type['url_name'])
    filename = os.path.join(BUFFER_DIR, page_type['url_name'] + '_data.zip')

    if need_load is None or need_load:
        loadNewData(page_type['url_name'], filename)

    if need_unzip is None or need_unzip:
        extractToDir(filename, dirname)

    for i, xml_file in enumerate(os.listdir(dirname)):
        if steps is not None and i >= steps:
            break
        if skip_steps is not None and i < skip_steps:
            continue
        print(f'{i}/{len(os.listdir(dirname))}')
        page_type['parse_func'](os.path.join(dirname, xml_file))



def fill():
    t = threading.Thread(target=__fill)
    t.start()


def __fill():
    print('FILL : global start...')

    Alive.objects.filter(still_alive=True).update(still_not_found=True)
    addToDB(PAGE_TYPES[0])
    Alive.objects.filter(still_not_found=True).update(
        date_disappear=datetime.now().date(),
        life_duration_years=datetime.now().date().year - Extract('date_create', 'year'),
        still_alive=False,
    )
    Alive.objects.filter(still_alive=True).update(
        life_duration_years=datetime.now().date().year - Extract('date_create', 'year'),
    )
    Alive.objects.filter(still_alive=False).update(still_not_found=False)
    addToDB(PAGE_TYPES[1])
    addToDB(PAGE_TYPES[2])
    addToDB(PAGE_TYPES[3])

    print('FILL : finish')


def test():
    t = threading.Thread(target=__test)
    t.start()


def __test():

    print('TEST : global start...')
    Alive.objects.filter(still_alive=True).update(still_not_found=True)
    addToDB(PAGE_TYPES[0], need_load=False, need_unzip=False)
    Alive.objects.filter(still_not_found=True).update(
        date_disappear=datetime.now().date(),
        life_duration_years=datetime.now().date().year - Extract('date_create', 'year'),
        still_alive=False,
    )
    Alive.objects.filter(still_alive=True).update(
        life_duration_years=datetime.now().date().year - Extract('date_create', 'year'),
    )
    Alive.objects.filter(still_alive=False).update(still_not_found=False)
    addToDB(PAGE_TYPES[1], need_load=False, need_unzip=False)
    addToDB(PAGE_TYPES[2], steps=30, need_load=False, need_unzip=False)
    addToDB(PAGE_TYPES[3], steps=30, need_load=False, need_unzip=False)
    print('TEST : finish')


def test_with_load():
    t = threading.Thread(target=__test_with_load)
    t.start()


def __test_with_load():
    print('TEST with load : global start...')
    Alive.objects.filter(still_alive=True).update(still_not_found=True)
    addToDB(PAGE_TYPES[0], steps=30, need_load=True, need_unzip=True)
    Alive.objects.filter(still_not_found=True).update(
        date_disappear=datetime.now().date(),
        life_duration_years=datetime.now().date().year - Extract('date_create', 'year'),
        still_alive=False,
    )
    Alive.objects.filter(still_alive=True).update(
        life_duration_years=datetime.now().date().year - Extract('date_create', 'year'),
    )
    Alive.objects.filter(still_alive=False).update(still_not_found=False)
    addToDB(PAGE_TYPES[1], steps=30, need_load=True, need_unzip=True)
    addToDB(PAGE_TYPES[2], steps=30, need_load=True, need_unzip=True)
    addToDB(PAGE_TYPES[3], steps=30, need_load=True, need_unzip=True)
    print('TEST with load : finish')


def foo():
    addToDB(PAGE_TYPES[0], steps=1, need_load=False, need_unzip=False)
    #
    # for x in range(100, 200):
    #     x = str(x)
    #     item = Company()
    #     item.inn = str(x)
    #     item.is_ip = True
    #     item.location_code = 10
    #     item.save()
    #
    # for f in Company._meta.fields:
    #     print(f)


# 'Государственная пошлина'
# 'Налог на игорный'
# 'Утилизационный сбор'

    #
    #
    #           6871 totasl
    #
    #
