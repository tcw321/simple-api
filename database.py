from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import StaticPool
import os

# Default database URL for production
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db/postgres")

def create_database_engine(db_url=None):
    """Create database engine with the given URL"""
    url = db_url or DATABASE_URL
    connect_args = {}
    
    # Add SQLite-specific configuration
    if url and url.startswith('sqlite'):
        connect_args["check_same_thread"] = False
    
    return create_engine(
        url,
        connect_args=connect_args,
        poolclass=StaticPool if url and url.startswith('sqlite') else None
    )

# Initialize engine and session maker
engine = None
SessionLocal = None

def init_db(db_url=None):
    """Initialize database connection"""
    global engine, SessionLocal
    
    # Don't reinitialize if already initialized with the same URL
    current_url = getattr(engine, 'url', None) if engine else None
    if engine and current_url == db_url:
        return engine
        
    engine = create_database_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine

Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    if SessionLocal is None:
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
