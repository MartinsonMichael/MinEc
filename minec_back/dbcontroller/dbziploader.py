import os
from bs4 import BeautifulSoup
import urllib.request
import requests
import zipfile
import maya
import traceback
from tqdm import tqdm
from dbcontroller.models import TaxBase, Company

BUFFER_DIR = './buffer/'


def loadNewData(name, filename):
    print('load data...')
    dataname = "www.nalog.ru/opendata/" + name
    html = requests.get("http://" + dataname).text
    soup = BeautifulSoup(html, 'html.parser')
    #print(soup.prettify())
    partwithdatalink = str(soup.find(text="Гиперссылка (URL) на набор").parent.parent)
    datalink = BeautifulSoup(partwithdatalink, 'html.parser').find('a').get('href')

    file = open(filename, 'wb')
    file.write(
        urllib.request.urlopen(datalink).read()
    )


def extractToDir(filename, dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    zip_ref = zipfile.ZipFile(filename, 'r')
    zip_ref.extractall(dirname)
    zip_ref.close()


def parseCompany(filename):
    print(f'start parse xml company {filename}')
    soup = BeautifulSoup(open(filename, 'r').read(), 'xml')
    buffer = []
    for item in soup.find_all('Документ'):
        try:

            main_part = item.find('ИПВклМСП')
            if main_part is None:
                main_part = item.find('ОргВклМСП')

            inn = None
            is_ip = None

            if main_part.has_attr('ИННФЛ'):
                inn = main_part['ИННФЛ']
                is_ip = True

            if main_part.has_attr('ИННЮЛ'):
                inn = main_part['ИННЮЛ']
                is_ip = False

            company = Company(
                inn=inn,
                is_ip=is_ip,
                date_create=maya.parse(item['ДатаВклМСП']).datetime(),
            )

            #location_code = item.find('СведМН')
            company.location_code = item.find('СведМН')['КодРегион']
            # for loc_type in location_code:
            #     setattr(
            #         company,
            #         str.lower(loc_type['Тип']),
            #         str.lower(loc_type['Наим'])
            #     )

            #company.save()
            buffer.append(company)
        except:
            print('Error while parsing:')
            print(item.prettify())
            print('\n***\nEroor:\n')
            traceback.print_exc()
            print('\n***\n')
            break

    Company.objects.bulk_create(buffer)

def parseNumEmployees(filename):
    print(f'start parse xml employee numbers {filename}')
    soup = BeautifulSoup(open(filename, 'r').read(), 'xml')

    cnt = 0
    pss = 0
    for item in soup.find_all('Документ'):
        cnt += 1
        try:
            inn = int(item.find('СведНП')['ИННЮЛ'])
            employee_num = int(item.find('СведССЧР')['КолРаб'])
            company = Company.objects.get(pk=inn)
            company.employee_num = employee_num
            company.save()
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

    buffer = []
    pss = 0
    cnt = 0
    for item in soup.find_all('Документ'):
        try:
            main_part = item.find('СведНП')

            inn = None

            if main_part.has_attr('ИННФЛ'):
                inn = main_part['ИННФЛ']

            if main_part.has_attr('ИННЮЛ'):
                inn = main_part['ИННЮЛ']

            if inn is None:
                continue

            company = Company.objects.get(pk=inn)

            tax_item = TaxBase(
                inn=company,
            )

            for tax in item.find_all('СвУплСумНал'):
                setattr(tax_item, tax['НаимНалог'], tax['СумУплНал'])

            buffer.append(tax_item)
            cnt += 1
        except Company.DoesNotExist:
            pss += 1
        except:
            print('Error while parsing:')
            print(item.prettify())
            print('\n***\nEroor:\n')
            traceback.print_exc()
            print('\n***\n')
            break
    TaxBase.objects.bulk_create(buffer)
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
        'parse_func': None,
    },
    {
        'name': 'НАЛОГИ',
        'url_name': '7707329152-paytax',
        'parse_func': parseTax,
    },
]


def addToDB(page_type, steps=None):
    print('start updating', page_type['name'])
    if not os.path.exists(BUFFER_DIR):
        os.makedirs(BUFFER_DIR)

    dirname = os.path.join(BUFFER_DIR, page_type['url_name'])
    filename = os.path.join(BUFFER_DIR, page_type['url_name'] + '_data.zip')

    loadNewData(page_type['url_name'], filename)
    extractToDir(filename, dirname)

    for i, xmlfile in enumerate(os.listdir(dirname)):
        print(f'{i}/{len(os.listdir(dirname))}')
        page_type['parse_func'](os.path.join(dirname, xmlfile))
        if steps is not None and i > steps:
            break



def test():
    print('global start...')
    print(os.path.abspath(os.path.curdir))

    addToDB(PAGE_TYPES[0], 10)

    addToDB(PAGE_TYPES[3], 10)

    # # addToDB(PAGE_TYPES[0])
    print('finish')


if __name__ == "__main__":
    test()
