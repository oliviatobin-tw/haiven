## Objective
Investigate the health of the `app-api` zone — the FastAPI endpoint handlers for chat, research,
creative matrix, multi-step, and key management features.

## Scope
Files in `app/api/**` (9 files):
- api_basics.py, api_company_research.py, api_creative_matrix.py
- api_features.py, api_key_management.py, api_multi_step.py
- api_rules.py, api_scenarios.py, boba_api.py

## Key Questions
- Do handlers separate concerns correctly (no business logic in endpoints)?
- Are type hints applied consistently to all parameters and return values?
- Are Pydantic models used for request/response validation?
- Is user input sanitised before being passed to LLMs?
- Are there any hardcoded secrets or credentials?
- Do files stay under the 300-line limit?

## Rules from CHARTER.yaml
- Allowed: separate handler files per domain, constructor DI, type hints, Pydantic validation
- Forbidden: business logic in endpoints, hardcoded credentials, unsanitised LLM input
- Max file lines: 300, target test coverage: 80%

## Expected Output
An assertion-backed markdown report (.a.md) with evidence for each assertion.
Use the assertion-backed-markdown skill to produce the report.
