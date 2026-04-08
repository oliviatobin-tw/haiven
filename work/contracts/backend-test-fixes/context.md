# Contract: backend-test-fixes

## Objective
Fix test infrastructure issues: mark integration tests correctly, fix or replace permanently skipped tests in test_server.py, and add missing tests for untested API endpoints.

## Scope
- app/tests/test_token_usage_integration.py — add @pytest.mark.integration markers
- app/tests/test_server.py — fix AsyncMock recursion issue and re-enable tests
- app/tests/test_api.py — add tests for /api/research and /api/features

## Source Reports
- backend-test-health.a.md: int-02, skip-01
- app-api-code-quality.a.md: test-01

## Constraints
- Do not remove the 5 skipped tests in test_server.py — fix them instead
- Tests must use the same test patterns established in existing test files (FastAPI TestClient, MagicMock/patch)
- Run: cd app && poetry run pytest -x --ignore=tests/test_server.py after each step; run test_server.py separately when fixing it
