# QA Execution Report

**Project:** TaskFlow API Testing & Validation Framework  
**Latest local execution:** 2026-11-12  
**Status:** All verified local quality gates passed. Remote GitHub Actions verification is pending repository publication.

## Latest verified execution

| Verification | Result |
|---|---:|
| Pytest cases | 34 passed, 0 failed |
| Python statement coverage | 97% |
| Pytest warnings | 0 |
| Newman requests | 13 executed, 0 failed |
| Newman assertions | 22 passed, 0 failed |
| Newman average response time | 63 ms |
| npm audit | 0 vulnerabilities |
| OpenAPI contract snapshot | Comparison passed |
| SQLite integrity | ok |
| SQLite foreign-key violations | 0 |
| Performance smoke samples | 40 requests to GET /health |
| Performance min / median / p95 / max | 3.68 / 5.41 / 29.05 / 32.12 ms |
| Performance p95 threshold | 500 ms, passed |

## Application runtime

- API server started successfully at http://127.0.0.1:8000.
- GET /health returned HTTP 200 with the expected service contract.
- Swagger UI is available at http://127.0.0.1:8000/docs.
- Newman completed the full collection twice: CLI/JUnit and HTML reporter runs both recorded 13 requests and 22 assertions with zero failures.

## Verified behavior

- Login with valid and invalid credentials.
- Missing, malformed, expired, and tampered bearer token rejection.
- Admin access and standard-user ownership isolation.
- Create, list, read, update, and delete task flows.
- Response keys and basic field types.
- Negative input, invalid enum, missing/extra fields, and title/description boundaries.
- Direct SQL persistence, foreign-key and CHECK constraints, and deletion verification.
- OpenAPI snapshot comparison detects schema drift.
- Performance smoke check samples endpoint latency and enforces a 500 ms p95 ceiling.

## Dependency remediation

The npm dependency tree uses compatible overrides for audited transitive packages. The patched Faker API is bridged to legacy names used by the upstream Postman collection SDK through a local compatibility adapter and idempotent postinstall patch. The current npm audit reports zero vulnerabilities.

The original Starlette/httpx test-client deprecation warning was resolved by using Starlette's supported httpx2 test-client transport. The latest Pytest run completed without warnings.

The upstream Newman dependency chain includes a deprecated transitive package notice for har-validator@5.1.5. This is an upstream maintenance warning; npm audit reports zero known vulnerabilities.

## Remaining caveats

- GitHub Actions is configured for OpenAPI drift, Pytest, performance, npm audit, and Newman. It has not yet run remotely; do not describe the workflow as green until the first remote run succeeds.
- Local runtime verification used Python 3.10. The GitHub Actions workflow targets Python 3.12, so compatibility must be confirmed by the remote workflow.
- Performance numbers are a low-volume local smoke sample, not load-test evidence.
- The API is a QA demonstration, not production identity infrastructure. The signing secret and seeded credentials are local demo values. Production use requires secret management, hardened token validation, rate limiting, TLS, and a mature identity provider.

## Conclusion

All local Python, Newman, dependency audit, database integrity, OpenAPI contract, and performance smoke checks passed on 2026-11-12. The authentication suite now explicitly covers malformed, expired, and tampered tokens. Remote CI status remains unverified until the repository is published and the workflow completes.
