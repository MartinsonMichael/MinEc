from decorator import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# prod
# psycorg_connect_string = 'postgresql://michael:123@db/minec_base_3'
# test
psycorg_connect_string = 'postgresql://michael:123@localhost/minec_base_3'

engine = create_engine(psycorg_connect_string)
Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)


def get_engine():
    return engine


def test_db_connection():
    import sqlalchemy as sqla
    from dbcontroller.models import TaxBase
    print('rows count in TaxBase:')
    with session_scope() as session:
        cnt = session.query(sqla.func.count(TaxBase.inn)).all()


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def sub_session_scope():
    engine2 = create_engine(psycorg_connect_string)
    Session2 = sessionmaker(bind=engine, autoflush=True, autocommit=False)
    session = Session2()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()