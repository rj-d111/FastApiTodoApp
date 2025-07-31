from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from ..database import Base
from sqlalchemy.orm import sessionmaker
from ..main import app
from fastapi.testclient import TestClient
import pytest
from datetime import datetime, timezone
from ..models import Users, Todos
from ..routers.auth import bcrypt_context


SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"id": 1, "username": "maria", "email": "maria@gmail.com", "role": "admin"}


client = TestClient(app)

@pytest.fixture
def test_todo():
    # Use a fixed datetime for consistency
    fixed_datetime = datetime(2023, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
    todo = Todos(
        title="Learn to code!",
        description="Complete the FastAPI tutorial",
        complete=False,
        date_created=fixed_datetime,
        date_modified=fixed_datetime,
        owner_id=1,
        id=1,
        archive=False,
        priority=1
    )
    
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    # Clean up using ORM to avoid raw SQL
    db.query(Todos).delete()
    db.commit()

@pytest.fixture
def test_user():
    user = Users(
        username="mary",
        email="mary@gmail.com",
        first_name="Mary",
        last_name="Smith",
        hashed_password=bcrypt_context.hash("mary123"),
        is_active=True,
        role="user",
        birthdate=datetime(1995, 5, 20).date(),
        phone_number="09123456789",
        gender = "female",
        country="Philippines",
    )
    
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    # Clean up using ORM to avoid raw SQL
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users;"))
        conn.commit()     