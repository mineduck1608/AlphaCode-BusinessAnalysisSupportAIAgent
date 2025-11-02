from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL kết nối
DATABASE_URL = "postgresql+psycopg2://postgres:123456@localhost:5432/mydb"

# Tạo engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True để in SQL ra console

# Base class cho ORM models
Base = declarative_base()

# Tạo Session
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
