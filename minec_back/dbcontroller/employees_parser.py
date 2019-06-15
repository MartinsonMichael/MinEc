from .AbstractFiller import AbstractFiller
from . import models


class EmployeesNumParser(AbstractFiller):

    def __init__(self, steps=None):
        super(EmployeesNumParser, self).__init__(cur_model=models.EmployeeNum, steps=steps)

    def parse_item(self, item=None):
        inn = item.find('СведНП')['ИННЮЛ']
        employee_num = int(item.find('СведССЧР')['КолРаб'])

        if models.Company.objects.filter(inn=inn).count() == 0:
            return None

        company = models.Company.objects.filter(inn=inn)[0]

        emp_item = models.EmployeeNum(
            _company=company,
            employee_num=employee_num,
        )
        return emp_item

