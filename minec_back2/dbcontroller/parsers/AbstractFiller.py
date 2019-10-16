import bs4
import time
import os
import datetime
from dbcontroller import models
from multiprocessing import Pool


class AbstractFiller:

    def __init__(self, cur_model, upd_date, steps=None):
        self.upd_date = upd_date
        self.cur_model = cur_model
        self.steps = steps
        self.base_name = cur_model.__name__
        self.MAX_SIZE_TO_CREATE = 15 * 10**3

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
            if True or q_add.filter(file_name=xml_file).count() == 0:
                try:
                    cur_items = self.parse_file(os.path.join(folder_name, xml_file))
                    to_create.extend(cur_items)
                    if self.steps is None:
                        schedule_item = models.ScheduleTable(
                            date=self.upd_date,
                            type='add',
                            base_name=self.base_name,
                            file_name=xml_file,
                        )
                        schedule_item.save()
                except:
                    everything_goes_well = False
            if len(to_create) > self.MAX_SIZE_TO_CREATE:
                self.save(to_create)
                to_create = []
        if len(to_create) != 0:
            self.save(to_create)
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
                    print('Error: no inn')
                    print(item.prettify())
                    continue
                inn_item = AbstractFiller.get_inn_element(inn)
                model_item = self.parse_item(inn_item, item)
                if model_item is None:
                    continue
                if isinstance(model_item, list):
                    to_create.extend(model_item)
                else:
                    to_create.append(model_item)
            except:
                print('Error while processing')
                print(item.prettify())
        return to_create

    def save(self, to_create):
        if len(to_create) == 0:
            return
        try:
            MAX_BATCH = 1000
            for i in range(0, len(to_create), MAX_BATCH):
                _from = i * MAX_BATCH
                _to = (i + 1) * MAX_BATCH
                try:
                    self.cur_model.objects.bulk_create(to_create[_from: _to])
                    self.add_upd_date(to_create[_from: _to])
                except:
                    for j in range(10):
                        _from2 = _from + j * MAX_BATCH / 10
                        _to2 = _from + (j + 1) * MAX_BATCH / 10
                        try:
                            self.cur_model.objects.bulk_create(to_create[_from2: _to2])
                            self.add_upd_date(to_create[_from2: _to2])
                        except:
                            for item in to_create[_from2: _to2]:
                                item.save()
                                self.add_upd_date([item])
            return
        except:
            to_add = []
            for item in to_create:
                try:
                    item.save()
                    to_add.append(item)
                except:
                    pass
            self.add_upd_date(to_add)

    def get_upd_date_set(self):
        return getattr(self.upd_date, self.cur_model.__name__.lower() + '_set')

    def add_upd_date(self, to_create):
        self.get_upd_date_set().add(*to_create)

    @staticmethod
    def get_inn(item):
        try:
            inn = item.find('ИПВклМСП')['ИННФЛ']
            if inn is not None:
                return inn
        except:
            pass
        try:
            inn = item.find('ОргВклМСП')['ИННЮЛ']
            if inn is not None:
                return inn
        except:
            pass
        try:
            inn = item.find('СведНП')['ИННЮЛ']
            if inn is not None:
                return inn
        except:
            pass
        try:
            main_part = item.find('СведНП')

            if main_part.has_attr('ИННФЛ'):
                inn = main_part['ИННФЛ']
                return inn

            if main_part.has_attr('ИННЮЛ'):
                inn = main_part['ИННЮЛ']
                return inn
        except:
            pass

        print('No inn', item.pretitfy(), sep='\n', end='\n')
        return None

    @staticmethod
    def get_inn_element(inn):
        try:
            inn_item = models.InnStore.objects.get(inn=inn)
            return inn_item
        except:
            inn_item = models.InnStore(inn=inn)
            inn_item.save()
            return inn_item

    def parse_item(self, inn, item=None):
        return None

    def extract_inn_list(self, folder_name):
        import pickle
        inn_list = []
        for i, xml_file in enumerate(os.listdir(folder_name)):
            if self.steps is not None and i >= self.steps:
                break
            soup = bs4.BeautifulSoup(open(os.path.join(folder_name, xml_file), 'r').read(), 'xml')
            for item in soup.find_all('Документ'):
                inn = AbstractFiller.get_inn(item)
                inn_list.append(inn)
            if i % 100 == 99:
                print(f'step : {i}')
            if i % 1000 == 999:
                pickle.dump(inn_list, open(f'inn_list__{self.cur_model.__name__}__{i}', 'wb'))
        pickle.dump(inn_list, open(f'inn_list__{self.cur_model.__name__}__all', 'wb'))
