from dbcontroller.parsers import AbstractFiller
from dbcontroller import models


class IncomeParser(AbstractFiller):

    def __init__(self, steps=None):
        super(IncomeParser, self).__init__(cur_model=models.BaseIncome, steps=steps)

    def parse_item(self, inn, item):
        if models.Company.objects.filter(inn=inn).count() == 0:
            return None
        company = models.Company.objects.filter(inn=inn)[0]

        item = item.find('СведДохРасх')
        income_item = models.BaseIncome(
            _company=company,
            income=item['СумДоход'],
            outcome=item['СумРасход'],
        )
        return income_item
