import bs4
import time
import os
import datetime
from . import models


class AbstractFiller:

    def __init__(self, cur_model, steps=None):
        self.cur_model = cur_model
        self.steps = steps
        self.base_name = cur_model.__name__

    def parse_folder(self, folder_name):
        q_add = models.ScheduleTable.objects\
            .filter(base_name=self.base_name)\
            .filter(date__gte=datetime.datetime.now().date() - datetime.timedelta(days=14))\
            .filter(type='add')

        everything_goes_well = True
        for i, xml_file in enumerate(os.listdir(folder_name)):
            if self.steps is not None and i >= self.steps:
                break
            if q_add.filter(file_name=xml_file).count() == 0:
                try:
                    self.parse_file(os.path.join(folder_name, xml_file))
                    schedule_item = models.ScheduleTable(
                        date=datetime.datetime.now().date(),
                        type='add',
                        base_name=self.base_name,
                        file_name=xml_file,
                    )
                    schedule_item.save()
                except:
                    everything_goes_well = False
        return everything_goes_well

    def parse_file(self, filename):
        print(f'start parse xml {self.cur_model.__name__} {filename}')
        now_time = time.time()
        soup = bs4.BeautifulSoup(open(filename, 'r').read(), 'xml')
        to_create = []
        for item in soup.find_all('Документ'):
            try:
                model_item = self.parse_item(item)
                if model_item is not None:
                    to_create.append(model_item)
            finally:
                pass
        self.cur_model.objects.bulk_create(to_create)

    def parse_item(self, item=None):
        return None
