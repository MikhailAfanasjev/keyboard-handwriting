import sqlalchemy as sql
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///db/db.db')
Base = declarative_base(bind=engine)
session = sessionmaker(bind=engine)()


class SaveDeleteModelMixin:
    def save(self):
        try:
            session.add(self)
            session.commit()
        except:
            session.rollback()
            raise
        return self

    def delete(self):
        session.delete(self)
        session.commit()


class User(Base, SaveDeleteModelMixin):
    __tablename__ = "user"

    password = sql.Column(sql.VARCHAR(16), primary_key=True)
    vector_min = sql.Column(sql.JSON)
    vector_max = sql.Column(sql.JSON)
