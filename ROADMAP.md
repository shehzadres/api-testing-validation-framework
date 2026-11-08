# Project 02 Roadmap

## Phase 1 - Core API and automated coverage
- [x] REST API with authentication and authorization
- [x] Task CRUD operations
- [x] Pydantic request validation and response schemas
- [x] SQLite schema and SQL constraints
- [x] Pytest integration suite
- [x] Postman collection and environment
- [x] Newman scripts and CI workflow

## Phase 2 - Local execution evidence
- [x] Install Python dependencies
- [x] Run Pytest and inspect failures
- [x] Generate HTML, JUnit, and coverage reports
- [x] Install Newman dependencies
- [x] Run live API collection and generate Newman reports
- [x] Verify database integrity
- [x] Verify clean npm ci installation
- [x] Resolve Python test-client deprecation warning
- [x] Remediate npm audit findings and verify 0 vulnerabilities
- [x] Smoke-test patched Newman Faker dynamic variables
- [x] Validate Postman JSON, environment JSON, and CI YAML
- [x] Add architecture diagram and request lifecycle documentation
- [x] Add 40-sample HTTP performance smoke check and JSON report
- [x] Add committed OpenAPI schema snapshot and drift detection
- [x] Integrate contract and performance gates into GitHub Actions
- [x] Capture sanitized Swagger and test-report screenshots
- [x] Re-run all local quality gates and regenerate Newman HTML/JUnit reports
- [x] Trace har-validator deprecation to upstream Newman/Postman dependency chain

## Phase 3 - Publication and remote verification
- [ ] Confirm target GitHub repository name and public/private visibility
- [ ] Publish local commit to the confirmed GitHub repository
- [ ] Run GitHub Actions remotely and inspect uploaded artifacts
- [ ] Revisit har-validator if upstream provides a compatible replacement

## Latest local execution evidence (2026-11-08)
- Pytest: 32 passed, 0 failed, 96% coverage, 0 warnings
- Newman: 13 requests, 22 assertions, 0 failures, 35 ms average
- Performance smoke: 40 requests, p95 26.10 ms, threshold 500 ms
- OpenAPI contract: snapshot comparison passed
- npm audit: 0 vulnerabilities
- SQLite integrity: ok; 0 foreign-key violations
- API health: HTTP 200
- GitHub Actions: configured and locally syntax-checked; remote run pending

## External dependency
The connected GitHub account is `shehzadres`. No existing repository for this project was found in the accessible repository list. A new repository must be created with a user-confirmed name and visibility before publishing. Local Git identity can use the account's verified noreply address; no global Git configuration is changed.

## Known caveats
- Local workstation has Python 3.10 only; CI is configured for Python 3.12 and must be verified remotely.
- Newman pulls deprecated `har-validator@5.1.5` through `postman-runtime -> postman-request`. A replacement override is not considered safe without upstream compatibility evidence.
- The performance sample is a smoke regression check, not a load or capacity benchmark.
