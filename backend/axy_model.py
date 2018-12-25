from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func, String
from sqlalchemy_utils import UUIDType

engine = create_engine('sqlite:///sqllite.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class User(Base):
	__tablename__ = 'users'
	id = Column(UUIDType(binary=False), primary_key=True)
	name = Column(Text)
	email = Column(Text)
	username = Column(String(255))