from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sqla
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy import create_engine

from dbcontroller.models_constants import REGION_TYPES, FEDERAL_TYPES


engine = create_engine('postgresql://michael:123@localhost/minec_base_3')

Base = declarative_base()

INN_SIZE = 24


class DateList(Base):
    __tablename__ = 'update_time'
    date = sqla.Column(sqla.Date, primary_key=True)


class InnStorage(Base):
    __tablename__ = 'all_inns'
    inn = sqla.Column(sqla.String(INN_SIZE), primary_key=True)


class Company(Base):
    __tablename__ = 'company'
    inn = sqla.Column(sqla.String(INN_SIZE), primary_key=True)
    upd_date = sqla.Column(sqla.Date, primary_key=True)

    # main fields
    is_ip = sqla.Column("является ИП", sqla.Boolean)
    short_title = sqla.Column("краткое название (не для ИП)", sqla.String(100))
    owner_name = sqla.Column("имя владельца (для ИП)", sqla.String(100))
    company_category = sqla.Column(
        "категория компании",
        ChoiceType([
            (0, 'тип не определн'),
            (1, 'микропредприятие'),
            (2, 'малое предприятие'),
            (3, 'среднее предприятие')
        ])
    )

    # location
    location_code = sqla.Column("код региона", sqla.Integer)
    region_name = sqla.Column("Название региона", ChoiceType(REGION_TYPES.items()),)
    federal_name = sqla.Column("федеральный округ", ChoiceType(FEDERAL_TYPES.items()), )


class EmployeeNum(Base):
    __tablename__ = 'employee_num'
    inn = sqla.Column(sqla.String(INN_SIZE), primary_key=True)
    upd_date = sqla.Column(sqla.Date, primary_key=True)
    employee_num = sqla.Column("количество работников", sqla.Integer)


#
# class OKVED(models.Model):
#     _inn = models.ForeignKey(InnStore, on_delete=models.CASCADE)
#     upd_date = models.ManyToManyField(LoadDates)
#     okved_code = models.TextField(verbose_name='Код ОКВЭД', max_length=21, null=True)
#     okved_code_name = models.TextField(verbose_name='Название ОКВЭД', max_length=160, null=True)
#     okved_is_prime = models.BooleanField(verbose_name='Основное ОКВЭД?', null=True)
#



#
# class TaxBase(models.Model):
#     _inn = models.ForeignKey(InnStore, on_delete=models.CASCADE)
#     upd_date = models.ManyToManyField(LoadDates)
#
#     tax_atribute_0 = models.FloatField(
#         verbose_name='Задолженность и перерасчеты по ОТМЕНЕННЫМ НАЛОГАМ'
#                      '  и сборам и иным обязательным платежам  (кроме ЕСН, страх. Взносов)',
#         default=0)
#     tax_atribute_1 = models.FloatField(verbose_name='Транспортный налог', default=0)
#     tax_atribute_2 = models.FloatField(verbose_name='Водный налог', default=0)
#     tax_atribute_3 = models.FloatField(
#         verbose_name='Налог, взимаемый в связи с  применением упрощенной  '
#                      'системы налогообложения', default=0)
#     tax_atribute_4 = models.FloatField(verbose_name='Налог на добавленную стоимость', default=0)
#     tax_atribute_5 = models.FloatField(verbose_name='Земельный налог', default=0)
#     tax_atribute_6 = models.FloatField(verbose_name='Акцизы, всего', default=0)
#     tax_atribute_7 = models.FloatField(verbose_name='НЕНАЛОГОВЫЕ ДОХОДЫ, '
#                                                     'администрируемые налоговыми органами',
#                                        default=0)
#     tax_atribute_8 = models.FloatField(verbose_name='Единый налог на вмененный '
#                                                     'доход для отдельных видов  деятельности',
#                                        default=0)
#     tax_atribute_9 = models.FloatField(verbose_name='Налог на добычу полезных ископаемых',
#                                        default=0)
#     tax_atribute_10 = models.FloatField(
#         verbose_name='Страховые и другие взносы на обязательное пенсионное страхование,'
#                      ' зачисляемые в Пенсионный фонд Российской Федерации',
#         default=0)
#     tax_atribute_11 = models.FloatField(
#         verbose_name='Страховые взносы на обязательное медицинское страхование '
#                      'работающего населения, зачисляемые в бюджет Федерального фонда '
#                      'обязательного медицинского страхования',
#         default=0)
#     tax_atribute_12 = models.FloatField(verbose_name='Налог на имущество организаций',
#                                         default=0)
#     tax_atribute_13 = models.FloatField(verbose_name='Налог на прибыль', default=0)
#     tax_atribute_14 = models.FloatField(verbose_name='Торговый сбор', default=0)
#     tax_atribute_15 = models.FloatField(verbose_name='Налог на доходы физических лиц',
#                                         default=0)
#     tax_atribute_16 = models.FloatField(verbose_name='Единый сельскохозяйственный налог',
#                                         default=0)
#     tax_atribute_17 = models.FloatField(
#         verbose_name='Сборы за пользование объектами животного мира  и за пользование '
#                      'объектами ВБР', default=0)
#     tax_atribute_18 = models.FloatField(
#         verbose_name='Страховые взносы на обязательное социальное страхование на случай'
#                      ' временной нетрудоспособности и в связи с материнством',
#         default=0)
#     tax_atribute_19 = models.FloatField(
#         verbose_name='Утилизационный сбор',
#         default=0)
#     tax_atribute_20 = models.FloatField(
#         verbose_name='Налог на игорный',
#         default=0)
#     tax_atribute_21 = models.FloatField(
#         verbose_name='Государственная пошлина',
#         default=0)
#
#
# class BaseIncome(models.Model):
#     _inn = models.ForeignKey(InnStore, on_delete=models.CASCADE)
#     upd_date = models.ManyToManyField(LoadDates)
#     income = models.FloatField('доход')
#     outcome = models.FloatField('расход')
#
#
#
#
#


Base.metadata.create_all(engine)