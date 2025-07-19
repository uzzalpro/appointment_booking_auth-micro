from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import config

SQLALCHEMY_DATABASE_URL = config.DATABASE_URL
SQLALCHEMY_DATABASE_SCHEMA = config.POSTGRES_SCHEMA

print("Database URL is ",SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)


def create_schemas():
    print("creating schema...")
    with engine.connect() as connection:
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SQLALCHEMY_DATABASE_SCHEMA}"))
        connection.commit()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
create_schemas()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()