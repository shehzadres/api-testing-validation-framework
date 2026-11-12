# API Test Plan

## Objective
Verify TaskFlow REST API behavior, contract stability, authentication and authorization boundaries, input validation, SQL persistence, and repeatable automated execution.

## Environment
- Python 3.10+
- Node.js 20+
- FastAPI service on 127.0.0.1:8000
- SQLite local database
- Postman/Newman and Pytest

## Test scenarios

| ID | Scenario | Expected |
|---|---|---|
| AUTH-01 | Login with valid user credentials | 200 + bearer token |
| AUTH-02 | Invalid password | 401 |
| AUTH-03 | Unknown username | 401 |
| AUTH-04 | Missing bearer token | 401 |
| AUTH-05 | Malformed token | 401 |
| AUTH-06 | Expired token | 401 |
| AUTH-07 | Tampered token signature | 401 |
| AUTH-08 | User reads another user's task | 403 |
| AUTH-09 | User updates/deletes another user's task | 403 |
| AUTH-10 | Admin reads another user's task | 200 |
| CRUD-01 | Create task | 201 + schema |
| CRUD-02 | List own tasks | 200 + owner-scoped data |
| CRUD-03 | Read existing task | 200 |
| CRUD-04 | Update task fields | 200 + updated values |
| CRUD-05 | Delete task | 204, subsequent GET 404 |
| VAL-01 | Title below minimum | 422 |
| VAL-02 | Title at minimum boundary | 201 |
| VAL-03 | Title at maximum boundary | 201 |
| VAL-04 | Title above maximum | 422 |
| VAL-05 | Description at maximum | 201 |
| VAL-06 | Description above maximum | 422 |
| VAL-07 | Invalid status | 422 |
| VAL-08 | Unexpected JSON property | 422 |
| VAL-09 | Empty patch | 400 |
| DB-01 | Created task persisted through SQL | Row exists |
| DB-02 | Orphan owner insert | FK violation |
| DB-03 | Invalid title direct insert | CHECK violation |
| DB-04 | Deleted task absent from SQL | Row absent |

## Execution strategy
1. Run the Pytest suite against an isolated SQLite database.
2. Run database integrity and foreign-key checks.
3. Start the API and execute the Postman collection with Newman.
4. Verify OpenAPI contract drift and performance smoke threshold.
5. Review HTML/JUnit reports.
6. CI executes Python tests first, then starts the service and runs Newman.

## Evidence policy
Only record pass/fail counts after an actual execution. Distinguish local results from remote CI results. A configured workflow or a collection definition is not proof that a remote pipeline passed.
