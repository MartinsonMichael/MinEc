from dbcontroller.model_constants import TAX_NAME_TO_ATTRIBUTE
from dbcontroller.models import TaxBase


def parse_tex(item, inn, upd_date):
    attributes = {
        'inn': inn,
        'upd_date': upd_date,
    }

    for tax in item.find_all('СвУплСумНал'):
        tax_name = TAX_NAME_TO_ATTRIBUTE[tax['НаимНалог']]
        if tax_name != 'tax_attribute_99':
            attributes.update({tax_name: tax['СумУплНал']})
        else:
            print(f"new tax : {tax['НаимНалог']}")

    return TaxBase(**attributes)
