import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from database import Base, init_db, get_db
from main import app

# Set testing environment
os.environ["TESTING"] = "1"

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

@pytest.fixture(scope="session", autouse=True)
def test_engine():
    """Create test database engine"""
    # Initialize the test database
    engine = init_db(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    # Return the engine
    yield engine
    
    # Clean up
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_db(test_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # Override the get_db dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Replace the dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Provide a database session
    db = TestingSessionLocal()
    yield db
    db.close()
    
    # Clean up the dependency override
    app.dependency_overrides.clear()

@pytest.fixture
def client(test_db):
    """Create test client"""
    with TestClient(app) as c:
        yield c
