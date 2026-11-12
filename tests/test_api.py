import sqlite3
import time
from pathlib import Path
import pytest
from app.main import encode_token

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "test_api.db"
TASK_KEYS = {"id", "title", "description", "status", "owner_id", "created_at", "updated_at"}

def test_health_contract(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "TaskFlow API", "version": "1.0.0"}

@pytest.mark.auth
@pytest.mark.parametrize("credentials", [
    {"username": "qa_user", "password": "User123!"},
    {"username": "admin", "password": "Admin123!"}
])
def test_valid_login(client, credentials):
    data = client.post("/auth/login", json=credentials).json()
    assert data["access_token"] and data["token_type"] == "bearer" and data["expires_in"] > 0

@pytest.mark.auth
@pytest.mark.parametrize("credentials", [
    {"username": "qa_user", "password": "wrong-pass"},
    {"username": "unknown_user", "password": "User123!"}
])
def test_invalid_login(client, credentials):
    assert client.post("/auth/login", json=credentials).status_code == 401

@pytest.mark.auth
def test_missing_token_rejected(client):
    assert client.get("/tasks").status_code == 401

@pytest.mark.auth
def test_malformed_token_rejected(client):
    assert client.get("/tasks", headers={"Authorization": "Bearer invalid.token.value"}).status_code == 401

@pytest.mark.auth
def test_expired_token_rejected(client):
    token = encode_token({"sub": 2, "username": "qa_user", "role": "user", "exp": int(time.time()) - 60})
    response = client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401

@pytest.mark.auth
def test_tampered_token_rejected(client):
    token = client.post("/auth/login", json={"username": "qa_user", "password": "User123!"}).json()["access_token"]
    header, payload, signature = token.split(".")
    replacement = ("A" if signature[0] != "A" else "B") + signature[1:]
    response = client.get("/tasks", headers={"Authorization": f"Bearer {header}.{payload}.{replacement}"})
    assert response.status_code == 401

@pytest.mark.auth
def test_user_cannot_read_another_users_task(client, auth_headers, second_user_token):
    task = client.post("/tasks", headers=auth_headers, json={"title": "Private task"}).json()
    headers = {"Authorization": f"Bearer {second_user_token}"}
    assert client.get(f"/tasks/{task['id']}", headers=headers).status_code == 403

@pytest.mark.auth
def test_user_cannot_update_or_delete_another_users_task(client, auth_headers, second_user_token):
    task = client.post("/tasks", headers=auth_headers, json={"title": "Protected task"}).json()
    headers = {"Authorization": f"Bearer {second_user_token}"}
    assert client.patch(f"/tasks/{task['id']}", headers=headers, json={"status": "completed"}).status_code == 403
    assert client.delete(f"/tasks/{task['id']}", headers=headers).status_code == 403

@pytest.mark.auth
def test_admin_can_read_any_users_task(client, admin_token, auth_headers):
    task = client.post("/tasks", headers=auth_headers, json={"title": "Admin visibility"}).json()
    headers = {"Authorization": f"Bearer {admin_token}"}
    assert client.get(f"/tasks/{task['id']}", headers=headers).status_code == 200

@pytest.mark.crud
def test_create_and_validate_response_schema(client, auth_headers):
    response = client.post("/tasks", headers=auth_headers, json={"title": "API contract", "description": "Schema validation"})
    assert response.status_code == 201
    data = response.json()
    assert set(data) == TASK_KEYS
    assert isinstance(data["id"], int) and data["title"] == "API contract"
    assert data["owner_id"] > 0 and data["created_at"] and data["updated_at"]

@pytest.mark.crud
def test_read_task(client, auth_headers, created_task):
    response = client.get(f"/tasks/{created_task['id']}", headers=auth_headers)
    assert response.status_code == 200 and response.json()["title"] == "Regression suite"

@pytest.mark.crud
def test_list_is_owner_scoped(client, created_task, second_user_token):
    response = client.get("/tasks", headers={"Authorization": f"Bearer {second_user_token}"})
    assert response.status_code == 200
    assert all(row["owner_id"] != created_task["owner_id"] for row in response.json())

@pytest.mark.crud
def test_update_task(client, auth_headers, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", headers=auth_headers, json={"title": "Updated regression", "status": "completed"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated regression" and response.json()["status"] == "completed"

@pytest.mark.crud
def test_delete_task(client, auth_headers, created_task):
    assert client.delete(f"/tasks/{created_task['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/tasks/{created_task['id']}", headers=auth_headers).status_code == 404

@pytest.mark.negative
@pytest.mark.parametrize("payload", [
    {"title": "ab"}, {"title": ""}, {"title": "x" * 121},
    {"title": "Valid title", "description": "d" * 501},
    {"title": "Valid title", "status": "blocked"},
    {"title": "Valid title", "unexpected": "field"}, {}
])
def test_invalid_payloads(client, auth_headers, payload):
    assert client.post("/tasks", headers=auth_headers, json=payload).status_code == 422

@pytest.mark.negative
def test_minimum_title_boundary(client, auth_headers):
    assert client.post("/tasks", headers=auth_headers, json={"title": "abc"}).status_code == 201

@pytest.mark.negative
def test_maximum_title_boundary(client, auth_headers):
    response = client.post("/tasks", headers=auth_headers, json={"title": "T" * 120})
    assert response.status_code == 201 and len(response.json()["title"]) == 120

@pytest.mark.negative
def test_maximum_description_boundary(client, auth_headers):
    response = client.post("/tasks", headers=auth_headers, json={"title": "Long description", "description": "D" * 500})
    assert response.status_code == 201 and len(response.json()["description"]) == 500

@pytest.mark.negative
def test_empty_patch_rejected(client, auth_headers, created_task):
    assert client.patch(f"/tasks/{created_task['id']}", headers=auth_headers, json={}).status_code == 400

@pytest.mark.negative
def test_null_only_patch_rejected(client, auth_headers, created_task):
    assert client.patch(f"/tasks/{created_task['id']}", headers=auth_headers, json={"title": None}).status_code == 400

@pytest.mark.negative
def test_nonexistent_task_returns_404(client, auth_headers):
    assert client.get("/tasks/999999", headers=auth_headers).status_code == 404

@pytest.mark.negative
def test_invalid_task_id_returns_422(client, auth_headers):
    assert client.get("/tasks/not-an-id", headers=auth_headers).status_code == 422

@pytest.mark.database
def test_task_persisted_in_sqlite(client, auth_headers):
    task_id = client.post("/tasks", headers=auth_headers, json={"title": "SQL persistence check"}).json()["id"]
    with sqlite3.connect(DB_PATH) as db:
        row = db.execute("SELECT id,title,status FROM tasks WHERE id=?", (task_id,)).fetchone()
    assert row == (task_id, "SQL persistence check", "pending")

@pytest.mark.database
def test_sql_foreign_key_and_check_constraints():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("PRAGMA foreign_keys=ON")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO tasks(title,owner_id) VALUES(?,?)", ("Orphan task", 999999))
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO tasks(title,owner_id) VALUES(?,?)", ("ab", 1))

@pytest.mark.database
def test_delete_removes_database_row(client, auth_headers, created_task):
    client.delete(f"/tasks/{created_task['id']}", headers=auth_headers)
    with sqlite3.connect(DB_PATH) as db:
        row = db.execute("SELECT id FROM tasks WHERE id=?", (created_task["id"],)).fetchone()
    assert row is None
