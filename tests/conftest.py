import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from database.session import get_session
from main import app
from models import User, Product  # ensure models are imported

@pytest.fixture(scope="function")
def client():
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    # Set environment variable for the app to use this db
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    # Re-create engine and tables? The app already imported, so we need to force it to use new URL.
    # We can reload the app module, but that's messy. Instead, we'll create our own engine and override.
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    # Clean up
    app.dependency_overrides.clear()
    # Close engine and delete file
    engine.dispose()
    os.unlink(db_path)

@pytest.fixture
def test_user():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }

@pytest.fixture
def auth_headers(client, test_user):
    client.post("/register", json=test_user)
    response = client.post(
        "/login",
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}