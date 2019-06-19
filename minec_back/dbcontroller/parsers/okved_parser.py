from dbcontroller.parsers import AbstractFiller
from dbcontroller import models


class OkvedParser(AbstractFiller):

    def __init__(self, steps=None, upd_date=None):
        super(OkvedParser, self).__init__(cur_model=models.OKVED, steps=steps, upd_date=upd_date)

    def parse_item(self, inn, item=None):
        buf = []

        company = models.Company.objects.filter(inn=inn)[0]
        # prime
        for okved in item.find('СвОКВЭД').findAll('СвОКВЭДОсн'):
            buf.append(models.OKVED(
                _company=company,
                _date=self.upd_date,
                code=okved['КодОКВЭД'],
                code_name=okved['НаимОКВЭД'],
                is_prime=True,
            ))
        # extra
        for okved in item.find('СвОКВЭД').findAll('СвОКВЭДДоп'):
            buf.append(models.OKVED(
                _company=company,
                upd_date=self.upd_date,
                code=okved['КодОКВЭД'],
                code_name=okved['НаимОКВЭД'],
                is_prime=True,
            ))
        return buf
