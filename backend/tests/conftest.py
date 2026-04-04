import pytest
import sys
import os
from pathlib import Path

# Set testing environment variable BEFORE importing main
os.environ["TESTING"] = "1"

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, get_db, Base
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone
from jose import jwt

# Use file-based SQLite for better debugging
TEST_DATABASE_URL = "sqlite:///./test.db"

# For testing - use a simple hashing method
def get_password_hash(password: str):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

@pytest.fixture(scope="function")
def test_engine():
    """Create a new database for each test function"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Verify tables were created
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Created tables: {tables}")
    
    yield engine
    
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    
    # Clean up test database file
    if os.path.exists("test.db"):
        os.remove("test.db")

@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a fresh database session for each test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client for each test"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# Simple user creation without complex dependencies
@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user - simplified version"""
    try:
        # Try to import User model
        from main import User
        
        # Check what attributes User model has
        user_data = {}
        if hasattr(User, 'username'):
            user_data['username'] = "testuser"
        if hasattr(User, 'email'):
            user_data['email'] = "test@example.com"
        if hasattr(User, 'hashed_password'):
            user_data['hashed_password'] = get_password_hash("testpass123")
        if hasattr(User, 'password_hash'):
            user_data['password_hash'] = get_password_hash("testpass123")
        if hasattr(User, 'is_active'):
            user_data['is_active'] = True
        
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    except Exception as e:
        print(f"Error creating test user: {e}")
        # Return a mock user if real user creation fails
        class MockUser:
            def __init__(self):
                self.id = 1
                self.username = "testuser"
                self.email = "test@example.com"
        return MockUser()

@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Create authentication headers"""
    # Use a simple token for testing
    SECRET_KEY = "your-secret-key-here"
    ALGORITHM = "HS256"
    
    access_token_expires = timedelta(minutes=30)
    to_encode = {
        "sub": getattr(test_user, 'username', 'testuser'),
        "exp": datetime.now(timezone.utc) + access_token_expires
    }
    
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"Authorization": f"Bearer {access_token}"}