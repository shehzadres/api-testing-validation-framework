# QA Execution Report

**Project:** TaskFlow API Testing & Validation Framework  
**Latest local execution:** 2026-11-08  
**Status:** All local quality gates passed. Remote GitHub Actions verification remains blocked only by repository destination/visibility confirmation.

## Latest verified execution

| Verification | Result |
|---|---:|
| Pytest cases | 32 passed, 0 failed |
| Python coverage | 96% |
| Pytest warnings | 0 |
| Newman requests | 13 executed, 0 failed |
| Newman assertions | 22 passed, 0 failed |
| Newman average response time | 42 ms |
| npm audit | 0 vulnerabilities |
| Faker compatibility smoke test | 4/4 generators passed after clean npm ci |
| SQLite integrity | ok |
| SQLite foreign-key violations | 0 |
| OpenAPI contract snapshot | Comparison passed |
| Performance smoke samples | 40 requests to GET /health |
| Performance min / median / p95 / max | 3.80 / 5.23 / 26.10 / 27.23 ms |
| Performance p95 threshold | 500 ms, passed |
| Postman JSON / environment / workflow YAML | Parsed successfully |

## Application runtime
- API server is running at http://127.0.0.1:8000.
- GET /health returned HTTP 200.
- GET /openapi.json returned HTTP 200.
- GET /docs returned HTTP 200; interactive Swagger UI was opened in Microsoft Edge.

## Evidence files
- reports/pytest-report.html
- reports/pytest-junit.xml
- reports/newman-report.html
- reports/newman-junit.xml
- reports/performance-smoke.json
- contracts/openapi.json
- docs/architecture.md
- docs/screenshots/swagger-ui.png
- docs/screenshots/pytest-report.png
- docs/screenshots/newman-report.png

## Verified behavior
- Login with valid and invalid credentials.
- Bearer-token requirement and malformed-token rejection.
- Admin access and standard-user ownership isolation.
- Create, list, read, update, and delete task flows.
- Response keys and basic field types.
- Negative input, invalid enum, missing/extra fields, and title/description boundaries.
- Direct SQL persistence, foreign-key and CHECK constraints, and deletion verification.
- OpenAPI snapshot comparison detects schema drift.
- Performance smoke check samples endpoint latency and enforces a 500 ms p95 ceiling.

## Dependency remediation
The original Newman dependency tree reported 21 advisories. Compatible npm overrides were added for affected transitive packages. The patched Faker API is bridged to the legacy names used by the upstream Postman collection SDK with a local compatibility adapter and idempotent postinstall patch. The postinstall smoke test verifies city, first-name, email, and UUID generators. A clean npm ci and npm audit --audit-level=moderate pass with zero vulnerabilities.

The original Starlette/httpx deprecation warning was resolved by replacing httpx with Starlette's supported httpx2 test-client transport. The latest Pytest run completes without warnings.

The remaining npm deprecation notice is traced to this upstream chain: newman -> postman-runtime -> postman-request -> har-validator@5.1.5. The package is deprecated upstream. No safe drop-in replacement was identified; a simple override can break the Postman request stack, so the dependency is documented rather than force-replaced. npm audit reports zero vulnerabilities.

## Remaining caveats
- GitHub Actions includes OpenAPI drift, Pytest, performance, npm audit, and Newman gates. Workflow YAML parses and equivalent local checks pass, but no remote workflow has run because the project has no configured GitHub remote.
- npm emits a deprecation notice for transitive har-validator@5.1.5. This is an upstream maintenance warning, not an npm audit vulnerability.
- The API is a QA demonstration, not production identity infrastructure. The signing secret and seeded credentials are local demo values. Production use requires secret management, hardened token validation, rate limiting, TLS, and a mature identity provider.
- Performance numbers are a low-volume local smoke sample, not load-test evidence.
- Local runtime verification used Python 3.10. The GitHub Actions workflow targets Python 3.12, which is not installed on this workstation and therefore still requires remote CI confirmation.

## Conclusion
All local Python, Newman, dependency, database, OpenAPI contract, and performance smoke checks passed in the latest execution. Do not describe GitHub Actions as green until a remote workflow run succeeds.

