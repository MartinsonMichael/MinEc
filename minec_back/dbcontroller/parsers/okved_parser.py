from dbcontroller.parsers import AbstractFiller
from dbcontroller import models


class OkvedParser(AbstractFiller):

    def __init__(self, steps=None, upd_date=None):
        super(OkvedParser, self).__init__(cur_model=models.OKVED, steps=steps, upd_date=upd_date)

    def parse_item(self, inn, item=None):
        buf = []

        # prime
        for okved in item.find('СвОКВЭД').findAll('СвОКВЭДОсн'):
            buf.append(models.OKVED(
                _inn=inn,
                okved_code=okved['КодОКВЭД'],
                okved_code_name=okved['НаимОКВЭД'],
                okved_is_prime=True,
            ))
        # extra
        for okved in item.find('СвОКВЭД').findAll('СвОКВЭДДоп'):
            buf.append(models.OKVED(
                _inn=inn,
                okved_code=okved['КодОКВЭД'],
                okved_code_name=okved['НаимОКВЭД'],
                okved_is_prime=False,
            ))
        return buf
