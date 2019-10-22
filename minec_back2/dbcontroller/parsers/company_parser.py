from dbcontroller.models import Company
from dbcontroller.model_constants import REGION_TYPES, REGION_TO_FEDERAL, COMPANY_TYPE


def parse_company(item, inn, upd_date):
    owner_name = None
    short_title = None
    is_ip = None
    company_category = int(item['КатСубМСП'])

    if item.find('ИПВклМСП') is not None:
        main_part = item.find('ИПВклМСП')
        is_ip = True
        owner_name = (" ".join(main_part.find('ФИОИП').attrs.values()))[:100]
        short_title = None

    if item.find('ОргВклМСП') is not None:
        main_part = item.find('ОргВклМСП')
        is_ip = False
        owner_name = None
        if main_part.has_attr('НаимОргСокр'):
            short_title = main_part['НаимОргСокр'][:100]
        elif main_part.has_attr('НаимОрг'):
            short_title = main_part['НаимОрг'][:100]
        else:
            short_title = None

    location_code = int(item.find('СведМН')['КодРегион'])
    company = Company(
        inn=inn,
        upd_date=upd_date,
        owner_name=owner_name,
        short_title=short_title,
        is_ip=is_ip,
        company_category=COMPANY_TYPE[company_category],
        location_code=location_code,
        region_name=REGION_TYPES[location_code],
        federal_name=REGION_TO_FEDERAL[REGION_TYPES[location_code]],
    )
    return company
