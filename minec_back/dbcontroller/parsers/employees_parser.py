from dbcontroller.parsers import AbstractFiller
from dbcontroller import models


class EmployeesNumParser(AbstractFiller):

    def __init__(self, steps=None, upd_date=None):
        super(EmployeesNumParser, self).__init__(cur_model=models.EmployeeNum, steps=steps, upd_date=upd_date)

    def parse_item(self, inn, item=None):
        employee_num = int(item.find('СведССЧР')['КолРаб'])

        if models.Company.objects.filter(inn=inn).count() == 0:
            return None

        company = models.Company.objects.filter(inn=inn)[0]

        emp_item = models.EmployeeNum(
            _company=company,
            _date=self.upd_date,
            employee_num=employee_num,
        )
        return emp_item

