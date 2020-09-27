# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from stock_analysis import settings

engine = create_engine(str(settings.SQLALCHEMY_DB_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(engine)


def get_session() -> Session:
    return SessionLocal()


def get_or_create(session: Session, obj: Base):
    model = type(obj)
    pk = model.__table__.primary_key.columns_autoinc_first[0].name
    v = getattr(obj, pk, None)
    condition = {pk: v}
    if v is not None and session.query(model).filter_by(**condition).count() != 0:
        del obj._sa_instance_state
        session.query(model).filter_by(**condition).update(values=obj.__dict__)
        session.commit()
        obj = session.query(model).filter_by(**condition).scalar()
        return obj, False
    else:
        session.add(obj)
        session.commit()
        session.flush()
        return obj, True
