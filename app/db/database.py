# app/db/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import psycopg2
# Load environment variables
load_dotenv()

# Get database configuration
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")


def _connect():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        sslmode='require',
        connect_timeout=10
    )

# 3) Engine from creator (DO NOT pass psycopg2.connect into create_engine)
engine = create_engine(
    "postgresql+psycopg2://",   # empty DSN on purpose
    creator=_connect,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    pool_recycle=300,           # avoid long-held sockets
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


