# -*- coding:utf-8 -*-

from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import Column, Integer, Float, String
import sys
import os

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)

import cores.utils as utils


class DB(object):
    db_file_path = os.path.join(root_path, 'db', 'TuJiDB.sqlite')
    if not os.path.exists(db_file_path):
        utils.create_path_tree(db_file_path)
    engine = create_engine("sqlite:///%s?check_same_thread=False" % db_file_path)
    Base = declarative_base()
    Session = sessionmaker(engine)
    session = Session()

    def __init__(self):
        if not os.path.exists(self.db_file_path):
            self.Base.metadata.create_all(self.engine)


class AreaTableBase(DB.Base):
    __tablename__ = 'area'
    id = Column(Integer, primary_key=True, autoincrement=True)
    lon = Column(Float)
    lat = Column(Float)
    type = Column(Integer, index=True)


class ContourTableBase(DB.Base):
    __tablename__ = 'contour'
    id = Column(Integer, primary_key=True, autoincrement=True)
    lon = Column(Float)
    lat = Column(Float)
    value = Column(Float)
    type = Column(Integer, index=True)


class RelationshipTableBase(DB.Base):
    __tablename__ = 'relationship'
    id = Column(Integer, primary_key=True, autoincrement=True)
    x = Column(Float)
    y = Column(Float)
    type = Column(Integer, index=True)


class TableOperator(DB):
    def to_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    @classmethod
    def insert_one(cls, commit=True, **kwargs):
        columns = [x.name for x in cls.__table__.columns]
        info = {}
        for k, v in kwargs.items():
            if k in columns:
                info[k] = v
        cls.session.add(cls(**info))
        if commit:
            cls.session.commit()

    @classmethod
    def insert_many(cls, items):
        for item in items:
            cls.insert_one(**item, commit=False)
        cls.session.commit()

    @classmethod
    def get_data(cls, column, value):
        return [x.to_dict() for x in cls.session.query(cls).filter(getattr(cls, column) == value)]


class AreaTable(AreaTableBase, TableOperator):
    pass


class ContourTable(ContourTableBase, TableOperator):
    pass


class RelationshipTable(RelationshipTableBase, TableOperator):
    pass


if __name__ == '__main__':
    db = DB()
