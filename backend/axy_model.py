from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func, String
from sqlalchemy_utils import UUIDType
import uuid

engine = create_engine('sqlite:///axy_sqllite.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class User(Base):
	__tablename__ = 'users'
	# TODO set binary=True is database supports UUID
	uuid = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
	name = Column(Text)
	email = Column(Text)
	username = Column(String(255))