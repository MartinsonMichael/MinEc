from dbcontroller.parsers import AbstractFiller
from dbcontroller import models
from dbcontroller import model_support
import datetime


class TaxParser(AbstractFiller):

    def __init__(self, steps=None):
        super(TaxParser, self).__init__(cur_model=models.TaxBase, steps=steps)
        self.TAX_DICT = model_support.create_TAX_DICT()

        # set add date to me even
        self._adding_date = datetime.datetime.now().date()
        if datetime.datetime.now().date().day % 2 == 1:
            self._adding_date = datetime.datetime.now().date() + datetime.timedelta(days=1)

    def parse_item(self, item=None):
        main_part = item.find('СведНП')
        inn = None

        if main_part.has_attr('ИННФЛ'):
            inn = main_part['ИННФЛ']

        if main_part.has_attr('ИННЮЛ'):
            inn = main_part['ИННЮЛ']

        if models.Company.objects.filter(inn=inn).count() == 0:
            return None

        print('inn found!')

        company = models.Company.objects.filter(inn=inn)[0]

        tax_item = models.TaxBase(
            _company=company,
            date=self._adding_date,
        )

        for tax in item.find_all('СвУплСумНал'):
            setattr(tax_item, self.TAX_DICT[tax['НаимНалог']], tax['СумУплНал'])

        return tax_item
