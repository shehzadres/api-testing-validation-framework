import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

TEST_DB = Path(__file__).resolve().parent.parent / "data" / "test_api.db"
TEST_DB.parent.mkdir(parents=True, exist_ok=True)
if TEST_DB.exists():
    TEST_DB.unlink()
os.environ["API_TEST_DB"] = str(TEST_DB)

from app.main import app, init_db

@pytest.fixture(scope="session")
def client():
    init_db()
    with TestClient(app) as test_client:
        yield test_client

def token(client, username, password):
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def admin_token(client):
    return token(client, "admin", "Admin123!")

@pytest.fixture
def user_token(client):
    return token(client, "qa_user", "User123!")

@pytest.fixture
def second_user_token(client):
    return token(client, "second_user", "User123!")

@pytest.fixture
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def created_task(client, auth_headers):
    response = client.post("/tasks", headers=auth_headers, json={"title": "Regression suite", "description": "Baseline API test"})
    assert response.status_code == 201
    return response.json()
