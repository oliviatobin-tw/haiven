## Objective
Investigate the quality, coverage, and TDD compliance of the backend test suite.

## Scope
Files in `app/tests/**` (49 test files) covering `app/api/**`, `app/llms/**`,
`app/knowledge/**`, `app/embeddings/**`, `app/prompts/**`, `app/auth/**`, `app/config/**`.

## Key Questions
- Are all major service classes and API handlers covered by unit tests?
- Are integration tests properly marked with @pytest.mark.integration?
- Are tests testing behaviour (not implementation details)?
- Is there evidence of TDD practice (tests close in age to production code)?
- Are there flaky or slow tests that could be improved?
- Are mocks used appropriately for external dependencies?

## Rules from CHARTER.yaml
- Target coverage: 80% for app-api, app-services, app-core
- Allowed: pytest fixtures, mocking external dependencies, pytest markers
- Forbidden: tests that depend on external services without mocking, skipping without explanation

## Expected Output
An assertion-backed markdown report (.a.md) with evidence for each assertion.
Use the assertion-backed-markdown skill to produce the report.
