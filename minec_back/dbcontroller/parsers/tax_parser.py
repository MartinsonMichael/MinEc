from dbcontroller.parsers import AbstractFiller
from dbcontroller import models
from dbcontroller import model_support
import datetime


class TaxParser(AbstractFiller):

    def __init__(self, steps=None, upd_date=None):
        super(TaxParser, self).__init__(cur_model=models.TaxBase, steps=steps, upd_date=upd_date)
        self.TAX_DICT = model_support.create_TAX_DICT()

    def parse_item(self, inn, item=None):

        tax_item = models.TaxBase(
            _company=inn,
        )

        for tax in item.find_all('СвУплСумНал'):
            setattr(tax_item, self.TAX_DICT[tax['НаимНалог']], tax['СумУплНал'])

        return tax_item
