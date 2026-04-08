# Contract: app-services-quick-fixes

## Objective
Fix small, safe code quality issues in the app-services zone (app/llms/, app/prompts/, app/knowledge/, app/embeddings/).

## Scope
- app/llms/aws_chat.py — delete dead code
- app/prompts/prompts.py — fix mutable default arguments
- app/knowledge/documents.py — fix class-level mutable state
- app/embeddings/documents.py — fix double get_extra_metadata() call

## Source Reports
- app-services-refactoring.a.md: llm-01, smell-01, smell-02, smell-03, smell-04

## Constraints
- Do NOT touch app/llms/chats.py or app/llms/clients.py (handled in split-chats-and-clients contract)
- Each task must be independently verifiable
- All tests must remain green after each change
