from dbcontroller.models import EmployeeNum


def parse_employee_num(item, inn, upd_date):
    employee_num = int(item.find('СведССЧР')['КолРаб'])
    return EmployeeNum(
        inn=inn,
        upd_date=upd_date,
        employee_num=employee_num,
    )

