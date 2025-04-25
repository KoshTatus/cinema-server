from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from src.models import Base

username = "postgres"
password = "12345"
host = "127.0.0.1"
port = "5438"
database_name = "postgres"

connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database_name}"

engine = create_engine(connection_string)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_tables():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()