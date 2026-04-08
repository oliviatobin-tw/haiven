# Contract: api-refactor

## Objective
Reduce api_basics.py from 669 lines, add Pydantic validation to api_company_research.py, add type hints to API constructors, and move inline prompt construction out of handlers.

## Scope
- app/api/api_basics.py — split into smaller files, extract prompt logic
- app/api/api_company_research.py — add Pydantic request model
- app/api/api_multi_step.py — extract prompt construction logic
- app/api/api_creative_matrix.py, api_scenarios.py — add type hints

## Source Reports
- app-api-code-quality.a.md: size-01, soc-01, soc-02, soc-03, pydantic-01, types-01, sec-01, sec-02, sec-03

## Constraints
- All endpoint URLs must remain unchanged
- Existing tests in test_api.py must continue to pass
- Prompt injection mitigations (sec-*) are noted but require careful architectural decisions — document the risk clearly in code comments as a minimum viable fix
