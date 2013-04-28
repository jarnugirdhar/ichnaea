from sqlalchemy import create_engine
from sqlalchemy import Column, Index, Integer, LargeBinary, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

_Model = declarative_base()


RADIO_TYPE = {
    'gsm': 0,
    'cdma': 1,
}


class Cell(_Model):
    __tablename__ = 'cell'
    __table_args__ = (
        Index('cell_idx', 'radio', 'mcc', 'mnc', 'lac', 'cid'),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8',
        }
    )

    id = Column(Integer, primary_key=True)
    # lat/lon * 1000000
    lat = Column(Integer)
    lon = Column(Integer)
    # mapped via RADIO_TYPE
    radio = Column(SmallInteger)
    # int in the range 0-1000
    mcc = Column(SmallInteger)
    # int in the range 0-1000 for gsm
    # int in the range 0-32767 for cdma (system id)
    mnc = Column(SmallInteger)
    lac = Column(Integer)
    cid = Column(Integer)
    range = Column(Integer)

cell_table = Cell.__table__


class Measure(_Model):
    __tablename__ = 'measure'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_row_format': 'compressed',
        'mysql_key_block_size': '4',
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    # lat/lon * 1000000
    lat = Column(Integer)
    lon = Column(Integer)
    accuracy = Column(SmallInteger)
    altitude = Column(SmallInteger)
    altitude_accuracy = Column(SmallInteger)
    radio = Column(SmallInteger)  # mapped via RADIO_TYPE
    # json blobs
    cell = Column(LargeBinary)
    wifi = Column(LargeBinary)

measure_table = Measure.__table__


class BaseDB(object):

    def __init__(self, sqluri):
        self.engine = create_engine(sqluri)
        self.session_factory = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False)

    def session(self):
        return self.session_factory()


class CellDB(BaseDB):

    def __init__(self, sqluri):
        super(CellDB, self).__init__(sqluri)
        cell_table.metadata.bind = self.engine
        cell_table.create(checkfirst=True)


class MeasureDB(BaseDB):

    def __init__(self, sqluri):
        super(MeasureDB, self).__init__(sqluri)
        self.sqluri = sqluri
        measure_table.metadata.bind = self.engine
        measure_table.create(checkfirst=True)
