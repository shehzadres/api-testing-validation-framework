# Session Context - Project 02

## Project
API Testing & Validation Framework, second project in the SQA portfolio.

## Location
C:\Users\Dell\Desktop\SQA-Portfolio\02-API-Testing-Validation-Framework

## Architecture
TaskFlow API built with FastAPI and SQLite. Postman/Newman covers live HTTP flows. Pytest covers integration, negative, boundary, authorization, and SQL-level checks. Additional gates compare generated OpenAPI to a committed snapshot and sample local HTTP health-check latency.

## Key files
- app/main.py: API, token handling, schema, SQLite access
- tests/test_api.py: automated suite
- tests/conftest.py: isolated test database and fixtures
- postman/TaskFlow_API.postman_collection.json: live API collection
- postman/local.postman_environment.json: local environment
- scripts/newman-faker-compat.cjs: adapter for legacy Postman SDK Faker calls
- scripts/patch-newman-faker.cjs: idempotent postinstall patch
- scripts/check-newman-faker.cjs: smoke test for patched Faker dynamic variables
- scripts/performance_smoke.py: 40-sample GET /health latency check
- scripts/openapi_contract.py: schema snapshot update and drift check
- contracts/openapi.json: committed API contract snapshot
- docs/architecture.md: Mermaid architecture and request lifecycle
- docs/screenshots/: Swagger and test-report screenshots
- .github/workflows/api-tests.yml: CI pipeline with contract, Python, performance, and Newman gates

## Latest verified state (2026-11-08)
- API running at http://127.0.0.1:8000; Swagger UI opened in Edge.
- Pytest: 32 passed, 0 failed; coverage 96%; zero warnings.
- Newman: 13 requests and 22 assertions, 0 failures; 42 ms average response time.
- npm ci succeeds; npm audit reports 0 vulnerabilities.
- Faker compatibility smoke test passes 4/4 generators after clean install.
- SQLite integrity: ok; no FK violations.
- OpenAPI snapshot comparison passes.
- Performance smoke: 40 samples; min 3.80 ms, median 5.23 ms, p95 26.10 ms, max 27.23 ms; 500 ms threshold passed.
- Swagger and report screenshots are saved in docs/screenshots/.
- API health endpoint returns HTTP 200.

## Remaining caveats
- GitHub Actions workflow is configured and syntax-checked but not remotely run; repository destination/visibility must be confirmed first.
- npm reports a deprecation notice for har-validator@5.1.5 through Newman -> Postman Runtime -> postman-request. No safe drop-in replacement was identified; npm audit still reports zero vulnerabilities.
- API secret and seed credentials are local demo values.
- Performance result is a small local smoke sample, not a load test or capacity benchmark.
- Local workstation runtime is Python 3.10; workflow targets Python 3.12 and requires remote CI verification.

## Next steps
1. Confirm repository name and public/private visibility, then publish.
2. Run remote GitHub Actions and inspect uploaded artifacts.
3. Review the upstream har-validator chain only when a compatible upstream fix is available.

