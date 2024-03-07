from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import AppConfig


engine = create_engine(AppConfig.DB_URI, future=True)
Session = sessionmaker(bind=engine, future=True)

Base = declarative_base()
