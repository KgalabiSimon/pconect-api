from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os, sys

load_dotenv()

def require(var):
    v = os.getenv(var)
    if not v:
        raise RuntimeError(f"Missing env var: {var}")
    return v

DB_HOST = require("DB_HOST")          # e.g. myserver.postgres.database.azure.com
DB_NAME = require("DB_NAME")          # e.g. pconnect
DB_USER = require("DB_USER")          # Flexible: appuser | Single: appuser@myserver
DB_PASSWORD = require("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

password = quote_plus(DB_PASSWORD)
# sslmode=require is needed for Azure
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

# If you still get SSL issues, you can also pass connect_args
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},  # psycopg2 understands this
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()