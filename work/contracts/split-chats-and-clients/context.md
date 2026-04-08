# Contract: split-chats-and-clients

## Objective
Split app/llms/chats.py (498 lines, 6 classes) into focused files and reduce function sizes in clients.py and chats.py.

## Scope
- app/llms/chats.py — split into multiple files, extract helpers from run_with_document()
- app/llms/clients.py — extract helpers from stream() (68 lines)

## Source Reports
- app-services-refactoring.a.md: size-01, size-02, size-04

## Constraints
- All imports that currently reference app.llms.chats must continue to work (update imports in all files)
- Run full test suite after each step: cd app && poetry run pytest -x --ignore=tests/test_server.py
- Do NOT touch app/prompts/prompts.py (handled in app-services-quick-fixes)
