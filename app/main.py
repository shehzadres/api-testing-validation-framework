import base64, hashlib, hmac, json, os, sqlite3, time
from contextlib import contextmanager
from pathlib import Path
from typing import Literal
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field

APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("API_TEST_DB", APP_DIR.parent / "data" / "api_testing.db"))
SECRET_KEY = os.getenv("API_SECRET_KEY", "local-testing-secret-change-before-deployment")
TOKEN_TTL_SECONDS = 3600
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
app = FastAPI(title="TaskFlow API", description="Task-management REST API for QA validation.", version="1.0.0")
security = HTTPBearer(auto_error=False)

def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return base64.urlsafe_b64encode(salt + digest).decode()

def verify_password(password: str, encoded: str) -> bool:
    try:
        raw = base64.urlsafe_b64decode(encoded.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), raw[:16], 120_000)
        return hmac.compare_digest(actual, raw[16:])
    except (ValueError, TypeError):
        return False

def encode_token(payload: dict) -> str:
    def part(value):
        return base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode()).decode().rstrip("=")
    body = f"{part({'alg': 'HS256', 'typ': 'JWT'})}.{part(payload)}"
    signature = hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest()
    return body + "." + base64.urlsafe_b64encode(signature).decode().rstrip("=")

def decode_token(token: str) -> dict:
    try:
        header, payload, signature = token.split(".")
        body = f"{header}.{payload}"
        expected = hmac.new(SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
        if not hmac.compare_digest(expected, supplied):
            raise ValueError("Invalid signature")
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        if data.get("exp", 0) < int(time.time()):
            raise ValueError("Expired token")
        return data
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

@contextmanager
def connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with connection() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL,
          role TEXT NOT NULL CHECK(role IN ('admin','user'))
        );
        CREATE TABLE IF NOT EXISTS tasks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL CHECK(length(title) BETWEEN 3 AND 120),
          description TEXT NOT NULL DEFAULT '' CHECK(length(description) <= 500),
          status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','in_progress','completed')),
          owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
        for username, password, role in [
            ("admin", "Admin123!", "admin"),
            ("qa_user", "User123!", "user"),
            ("second_user", "User123!", "user")
        ]:
            db.execute("INSERT OR IGNORE INTO users(username,password_hash,role) VALUES(?,?,?)",
                       (username, hash_password(password), role))

init_db()

class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    password: str = Field(min_length=8, max_length=128)

class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(default="", max_length=500)
    status: Literal["pending", "in_progress", "completed"] = "pending"

class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    status: Literal["pending", "in_progress", "completed"] | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    owner_id: int
    created_at: str
    updated_at: str

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Bearer token required")
    data = decode_token(credentials.credentials)
    with connection() as db:
        user = db.execute("SELECT id,username,role FROM users WHERE id=?", (data.get("sub"),)).fetchone()
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return dict(user)

def task_or_404(db, task_id):
    task = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

def visible_task(task, user):
    if user["role"] != "admin" and task["owner_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="You cannot access another user's task")
    return task

@app.get("/health")
def health():
    return {"status": "ok", "service": "TaskFlow API", "version": "1.0.0"}

@app.post("/auth/login")
def login(body: LoginRequest):
    with connection() as db:
        user = db.execute("SELECT * FROM users WHERE username=?", (body.username,)).fetchone()
    if user is None or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    now = int(time.time())
    token = encode_token({"sub": user["id"], "username": user["username"], "role": user["role"], "iat": now, "exp": now + TOKEN_TTL_SECONDS})
    return {"access_token": token, "token_type": "bearer", "expires_in": TOKEN_TTL_SECONDS, "role": user["role"]}

@app.get("/auth/me")
def me(user: dict = Depends(current_user)):
    return user

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(body: TaskCreate, user: dict = Depends(current_user)):
    with connection() as db:
        cursor = db.execute("INSERT INTO tasks(title,description,status,owner_id) VALUES(?,?,?,?)",
                             (body.title, body.description, body.status, user["id"]))
        task = task_or_404(db, cursor.lastrowid)
    return dict(task)

@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(user: dict = Depends(current_user)):
    with connection() as db:
        rows = db.execute("SELECT * FROM tasks ORDER BY id") .fetchall() if user["role"] == "admin" else db.execute("SELECT * FROM tasks WHERE owner_id=? ORDER BY id", (user["id"],)).fetchall()
    return [dict(row) for row in rows]

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, user: dict = Depends(current_user)):
    with connection() as db:
        task = visible_task(task_or_404(db, task_id), user)
    return dict(task)

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, body: TaskUpdate, user: dict = Depends(current_user)):
    changes = body.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="At least one field must be supplied")
    with connection() as db:
        visible_task(task_or_404(db, task_id), user)
        values = {key: value for key, value in changes.items() if value is not None}
        if not values:
            raise HTTPException(status_code=400, detail="At least one non-null field must be supplied")
        assignments = ", ".join(f"{key}=?" for key in values)
        db.execute(f"UPDATE tasks SET {assignments},updated_at=CURRENT_TIMESTAMP WHERE id=?", (*values.values(), task_id))
        updated = task_or_404(db, task_id)
    return dict(updated)

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, user: dict = Depends(current_user)):
    with connection() as db:
        visible_task(task_or_404(db, task_id), user)
        db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    return None
