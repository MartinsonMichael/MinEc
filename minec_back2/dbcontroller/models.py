from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sqla
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy import create_engine

from dbcontroller.model_constants import REGION_TYPES, FEDERAL_TYPES, COMPANY_TYPE
from dbcontroller.session_contoller import get_engine, session_scope

Base = declarative_base()

INN_SIZE = 24


class DateList(Base):
    __tablename__ = 'update_time'
    date = sqla.Column('upd_date', sqla.Date, primary_key=True)


class Company(Base):
    __tablename__ = 'company'
    inn = sqla.Column('inn', sqla.String(INN_SIZE), primary_key=True)
    upd_date = sqla.Column('upd_date', sqla.Date, primary_key=True)

    # main fields
    is_ip = sqla.Column('is_ip', sqla.Boolean)
    short_title = sqla.Column('short_title', sqla.String(100))
    owner_name = sqla.Column('owner_name', sqla.String(100))
    company_category = sqla.Column('company_category', ChoiceType([(v, k) for k, v in COMPANY_TYPE.items()]))

    # location
    location_code = sqla.Column('region_code', sqla.Integer)
    region_name = sqla.Column('region_name', ChoiceType([(v, k) for k, v in REGION_TYPES.items()]), )
    federal_name = sqla.Column('federal_name', ChoiceType([(v, k) for k, v in FEDERAL_TYPES.items()]), )


class EmployeeNum(Base):
    __tablename__ = 'employee'
    inn = sqla.Column('inn', sqla.String(INN_SIZE), primary_key=True)
    upd_date = sqla.Column('upd_date', sqla.Date, primary_key=True)
    employee_num = sqla.Column('employee_num', sqla.Integer)


class OKVED(Base):
    __tablename__ = 'okved'
    inn = sqla.Column('inn', sqla.String(INN_SIZE), primary_key=True)
    upd_date = sqla.Column('upd_date', sqla.Date, primary_key=True)

    okved_code = sqla.Column('okved_code', sqla.String(21))
    okved_code_name = sqla.Column('okved_title', sqla.String(120))
    okved_is_prime = sqla.Column('okved_is_prime', sqla.Boolean)


class TaxBase(Base):
    __tablename__ = 'taxes'
    inn = sqla.Column('inn', sqla.String(INN_SIZE), primary_key=True)
    upd_date = sqla.Column('upd_date', sqla.Date, primary_key=True)

    tax_attribute_0 = sqla.Column('tax_attribute_0', sqla.Float)
    tax_attribute_1 = sqla.Column('tax_attribute_1', sqla.Float)
    tax_attribute_2 = sqla.Column('tax_attribute_2', sqla.Float)
    tax_attribute_3 = sqla.Column('tax_attribute_3', sqla.Float)
    tax_attribute_4 = sqla.Column('tax_attribute_4', sqla.Float)
    tax_attribute_5 = sqla.Column('tax_attribute_5', sqla.Float)
    tax_attribute_6 = sqla.Column('tax_attribute_6', sqla.Float)
    tax_attribute_7 = sqla.Column('tax_attribute_7', sqla.Float)
    tax_attribute_8 = sqla.Column('tax_attribute_8', sqla.Float)
    tax_attribute_9 = sqla.Column('tax_attribute_9', sqla.Float)
    tax_attribute_10 = sqla.Column('tax_attribute_10', sqla.Float)
    tax_attribute_11 = sqla.Column('tax_attribute_11', sqla.Float)
    tax_attribute_12 = sqla.Column('tax_attribute_12', sqla.Float)
    tax_attribute_13 = sqla.Column('tax_attribute_13', sqla.Float)
    tax_attribute_14 = sqla.Column('tax_attribute_14', sqla.Float)
    tax_attribute_15 = sqla.Column('tax_attribute_15', sqla.Float)
    tax_attribute_16 = sqla.Column('tax_attribute_16', sqla.Float)
    tax_attribute_17 = sqla.Column('tax_attribute_17', sqla.Float)
    tax_attribute_18 = sqla.Column('tax_attribute_18', sqla.Float)
    tax_attribute_19 = sqla.Column('tax_attribute_19', sqla.Float)
    tax_attribute_20 = sqla.Column('tax_attribute_20', sqla.Float)
    tax_attribute_21 = sqla.Column('tax_attribute_21', sqla.Float)


class BaseIncome(Base):
    __tablename__ = 'income'
    inn = sqla.Column('inn', sqla.String(INN_SIZE), primary_key=True)
    upd_date = sqla.Column('upd_date', sqla.Date, primary_key=True)

    income = sqla.Column('income', sqla.Float)
    outcome = sqla.Column('outcome', sqla.Float)


USED_TABLES_NAME = ['company', 'taxes', 'income', 'okved', 'employee']
USED_TABLES = [Company, TaxBase, BaseIncome, OKVED, EmployeeNum]
ALL_TABLES = [Company, TaxBase, BaseIncome, OKVED, EmployeeNum, DateList]


def get_upd_date_list():
    with session_scope() as session:
        return session.query(DateList.date).all()


Base.metadata.create_all(get_engine())
