# Project 02: API Testing & Validation Framework

A portfolio-grade API quality engineering project demonstrating functional, contract, security, negative, boundary, database, and basic performance testing against a realistic REST API.

## Technology
- API under test: FastAPI, REST, OpenAPI
- API client suite: Postman collection + Newman CLI
- Automation: Python, Pytest, FastAPI TestClient
- Database: SQLite with direct SQL verification and integrity constraints
- Contract: committed OpenAPI schema snapshot with drift detection
- Performance: repeatable HTTP health-endpoint smoke check
- Reporting: Pytest HTML/JUnit, coverage, Newman CLI/JUnit/HTML, performance JSON
- CI: GitHub Actions

## Architecture
TaskFlow is a task-management service with seeded admin, qa_user, and second_user accounts. Passwords are PBKDF2-hashed. Authentication uses signed, expiring bearer tokens. Regular users can access only their own tasks; administrators can access all tasks.

See [architecture diagram and request lifecycle](docs/architecture.md).

| Area | Coverage |
|---|---|
| Authentication | Valid/invalid login, missing/malformed token |
| Authorization | Owner isolation, admin visibility, cross-user update/delete |
| CRUD | Create, list, get, patch, delete |
| Contract | Required response keys, value types, OpenAPI snapshot drift |
| Negative | Missing fields, extra fields, invalid enum, malformed IDs |
| Boundary | Title 3/120 chars, description 500 chars |
| Database | Persistence, FK/check constraints, delete verification |
| Performance | 40-request GET /health smoke sample, p95 threshold |
| Automation | Pytest, Newman, GitHub Actions |

## Quick start (Windows PowerShell)

    py -m venv .venv
    New-Item -ItemType Directory -Force reports | Out-Null
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    pytest -v --html=reports/pytest-report.html --self-contained-html --junitxml=reports/pytest-junit.xml --cov=app --cov-report=term-missing

## Run the API

    python -m uvicorn app.main:app --reload

OpenAPI documentation: http://127.0.0.1:8000/docs

## Run contract and performance checks

    npm run contract:check
    npm run performance:smoke

The OpenAPI check compares the generated schema to contracts/openapi.json. If an intentional API change modifies the schema, review the diff and regenerate the snapshot with:

    python scripts/openapi_contract.py --update

The performance smoke check sends 40 sequential requests to GET /health, reports min/median/p95/max latency, and enforces a 500 ms p95 ceiling. This is a regression smoke test, not a load or capacity benchmark.

## Run Postman + Newman

Install Node.js, then:

    npm ci
    npm audit --audit-level=moderate
    npm run postman:test
    npm run postman:html

The collection uses postman/local.postman_environment.json. Start the API before running Newman. The collection performs login, CRUD, response assertions, validation checks, and authorization checks.

## Demo credentials

| Role | Username | Password |
|---|---|---|
| Administrator | admin | Admin123! |
| Standard user | qa_user | User123! |
| Standard user | second_user | User123! |

These are local demo credentials only. Never reuse them in a deployed environment.

## Database verification

    python scripts/db_check.py

The test suite uses an isolated database at data/test_api.db; normal API runs use data/api_testing.db. Both are ignored by Git.

## Reports
- reports/pytest-report.html: human-readable Python test report
- reports/pytest-junit.xml: CI-compatible test results
- reports/newman-report.html: Postman/Newman HTML report
- reports/newman-junit.xml: Newman JUnit output
- reports/performance-smoke.json: latency sample summary

## Quality gates
GitHub Actions checks the OpenAPI snapshot and Pytest suite, then starts the API, runs the performance smoke check, audits Node dependencies, and executes Newman. CI artifacts are uploaded even when a test step fails.

## Dependency security and compatibility

The npm dependency tree is protected with compatible overrides for audited transitive packages. Run npm audit --audit-level=moderate after npm ci; the current lockfile audits with zero vulnerabilities.

The Postman SDK still calls legacy Faker APIs. The project therefore pins a patched Faker version and applies a small compatibility adapter during npm ci via the postinstall script. The postinstall smoke test verifies representative dynamic variables. Do not remove the overrides or compatibility scripts without rerunning the Newman suite.

Python uses httpx2, the current Starlette TestClient transport, to avoid the deprecated httpx integration.

## Security and scope notes
This is a deliberately scoped QA demonstration, not a production-ready identity platform. The signing secret is a local development default, the seed accounts are public demo credentials, and rate limiting, refresh tokens, password reset, TLS termination, and production secret management are outside this project's scope.
