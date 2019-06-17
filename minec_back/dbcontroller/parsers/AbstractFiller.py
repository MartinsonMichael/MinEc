import bs4
import time
import os
import datetime
from dbcontroller import models


class AbstractFiller:

    def __init__(self, cur_model, steps=None):
        self.cur_model = cur_model
        self.steps = steps
        self.base_name = cur_model.__name__
        self.MAX_SIZE_TO_CREATE = 5 * 10**3

    def parse_folder(self, folder_name):
        q_add = models.ScheduleTable.objects\
            .filter(base_name=self.base_name)\
            .filter(date__gte=datetime.datetime.now().date() - datetime.timedelta(days=14))\
            .filter(type='add')

        everything_goes_well = True
        to_create = []
        for i, xml_file in enumerate(os.listdir(folder_name)):
            if self.steps is not None and i >= self.steps:
                break
            if q_add.filter(file_name=xml_file).count() == 0:
                try:
                    cur_items = self.parse_file(os.path.join(folder_name, xml_file))
                    to_create.extend(cur_items)
                    if self.steps is None:
                        schedule_item = models.ScheduleTable(
                            date=datetime.datetime.now().date(),
                            type='add',
                            base_name=self.base_name,
                            file_name=xml_file,
                        )
                        schedule_item.save()
                except:
                    everything_goes_well = False
            if len(to_create) > self.MAX_SIZE_TO_CREATE:
                self.cur_model.objects.bulk_create(to_create, batch_size=500)
                to_create = []
        if len(to_create) != 0:
            self.cur_model.objects.bulk_create(to_create, batch_size=500)
        return everything_goes_well

    def parse_file(self, filename):
        print(f'start parse xml {self.cur_model.__name__} {filename}')
        now_time = time.time()
        soup = bs4.BeautifulSoup(open(filename, 'r').read(), 'xml')
        to_create = []
        for item in soup.find_all('Документ'):
            try:
                inn = AbstractFiller.get_inn(item)
                if inn is None:
                    continue
                model_item = self.parse_item(inn, item)
                if model_item is None:
                    continue
                if isinstance(model_item, list):
                    to_create.extend(model_item)
                else:
                    to_create.append(model_item)
            finally:
                pass
        #self.cur_model.objects.bulk_create(to_create)
        return to_create

    @staticmethod
    def get_inn(item):
        try:
            return item.find('ИПВклМСП')['ИННФЛ']
        except:
            pass
        try:
            return item.find('ОргВклМСП')['ИННЮЛ']
        except:
            pass
        try:
            return item.find('СведНП')['ИННЮЛ']
        except:
            pass
        print(item.pretitfy(), file=open('have_no_inn', 'w+'))
        return None

    def parse_item(self, inn, item=None):
        return None
