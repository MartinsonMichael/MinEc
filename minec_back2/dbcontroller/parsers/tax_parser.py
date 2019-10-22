from dbcontroller.model_constants import TAX_NAME_TO_ATTRIBUTE
from dbcontroller.models import TaxBase


def parse_tex(item, inn, upd_date):
    attributes = {
        'inn': inn,
        'upd_date': upd_date,
    }

    for tax in item.find_all('СвУплСумНал'):
        attributes.update({TAX_NAME_TO_ATTRIBUTE[tax['НаимНалог']]: tax['СумУплНал']})

    return TaxBase(**attributes)
