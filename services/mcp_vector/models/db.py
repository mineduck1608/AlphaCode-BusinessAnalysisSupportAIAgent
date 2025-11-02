import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# load biến môi trường từ file .env
load_dotenv()
# URL kết nối
DATABASE_URL = os.getenv('DB_URL')

# Tạo engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True để in SQL ra console

# Base class cho ORM models
Base = declarative_base()

# Tạo Session
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
