from decorator import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://michael:123@db/minec_base_3')
Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)


def get_engine():
    return engine


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
