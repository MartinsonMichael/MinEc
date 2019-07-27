from dbcontroller.parsers import AbstractFiller
from dbcontroller import models


class IncomeParser(AbstractFiller):

    def __init__(self, steps=None, upd_date=None):
        super(IncomeParser, self).__init__(cur_model=models.BaseIncome, steps=steps, upd_date=upd_date)

    def parse_item(self, inn, item=None):
        item = item.find('СведДохРасх')
        income_item = models.BaseIncome(
            _inn=inn,
            income=item['СумДоход'],
            outcome=item['СумРасход'],
        )
        return income_item
