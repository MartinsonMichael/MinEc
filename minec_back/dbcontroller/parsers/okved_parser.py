from dbcontroller.parsers import AbstractFiller
from dbcontroller import models


class CompanyMainParser(AbstractFiller):

    def __init__(self, steps=None):
        super(CompanyMainParser, self).__init__(cur_model=models.OKVED, steps=steps)

    def parse_item(self, item):
        pass
