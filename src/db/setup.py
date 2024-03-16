from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import config

engine = create_engine(config.get_db_uri(), future=True)
Session = sessionmaker(bind=engine, future=True)

Base = declarative_base()
