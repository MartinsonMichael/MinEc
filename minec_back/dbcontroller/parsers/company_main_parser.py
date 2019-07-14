from dbcontroller.parsers import AbstractFiller
from dbcontroller import models
from dbcontroller import model_support


class CompanyMainParser(AbstractFiller):

    def __init__(self, steps=None, upd_date=None):
        super(CompanyMainParser, self).__init__(
            cur_model=models.Company,
            steps=steps,
            upd_date=upd_date
        )
        self.ASK_DICT = model_support.create_ASK_DICT()
        self.old_companies = []

    def parse_item(self, inn, item=None):
        owner_name = None
        short_title = None
        is_ip = None

        company_category = self.ASK_DICT['company__company_category']['machine_mapper'][
            int(item['КатСубМСП'])
        ]

        if item.find('ИПВклМСП') is not None:
            main_part = item.find('ИПВклМСП')
            is_ip = True
            owner_name = " ".join(main_part.find('ФИОИП').attrs.values())
            short_title = None

        if item.find('ОргВклМСП') is not None:
            main_part = item.find('ОргВклМСП')
            is_ip = False
            owner_name = None
            if main_part.has_attr('НаимОргСокр'):
                short_title = main_part['НаимОргСокр']
            elif main_part.has_attr('НаимОрг'):
                short_title = main_part['НаимОрг']
            else:
                short_title = None

        if models.Company.objects.filter(inn=inn).count() > 0:
            self.old_companies.append(inn)
            return None

        location_code = int(item.find('СведМН')['КодРегион'])
        company = models.Company(
            inn=inn,
            owner_name=owner_name,
            short_title=short_title,
            is_ip=is_ip,
            company_category=company_category,
            location_code=location_code,
            region_name=models.REGION_TYPES[location_code],
            federal_name=models.REGION_TO_FEDERAL[models.REGION_TYPES[location_code]],
        )
        return company

    def on_folder_end(self):
        self.get_upd_date_set().add(
            *models.Company.objects.filter(inn__in=self.old_companies)
        )
