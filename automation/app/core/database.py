from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from app.core.config import settings

# Standard Sync Engine using psycopg2
engine = create_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,
    echo=True  # Logs SQL queries; set to False in production
)

# Sync Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for declarative SQLAlchemy Models
class Base(DeclarativeBase):
    pass

# Dependency Injection for FastAPI Endpoints
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()