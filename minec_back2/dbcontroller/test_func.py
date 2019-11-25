from dbcontroller.parsers import parse_folder
from datetime import date
from dbcontroller.parsers import parse_company


def fill_base():
    parse_folder('./data/.', date(year=2019, month=10, day=18), parse_company)

