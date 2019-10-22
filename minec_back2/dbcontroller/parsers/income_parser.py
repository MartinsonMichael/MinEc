from dbcontroller.models import BaseIncome


def parse_income(item, inn, upd_date):
    item = item.find('СведДохРасх')
    return BaseIncome(
        inn=inn,
        upd_date=upd_date,
        income=item['СумДоход'],
        outcome=item['СумРасход'],
    )
