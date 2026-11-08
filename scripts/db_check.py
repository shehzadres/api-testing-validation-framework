import os, sqlite3
from pathlib import Path

db_path = Path(os.getenv("API_TEST_DB", "data/api_testing.db"))
if not db_path.exists():
    raise SystemExit(f"Database not found: {db_path}")
with sqlite3.connect(db_path) as db:
    integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    tasks = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    foreign_key_errors = db.execute("PRAGMA foreign_key_check").fetchall()
print(f"Database: {db_path.resolve()}")
print(f"Integrity: {integrity}")
print(f"Users: {users}")
print(f"Tasks: {tasks}")
print(f"Foreign-key violations: {len(foreign_key_errors)}")
if integrity != "ok" or foreign_key_errors:
    raise SystemExit(1)
