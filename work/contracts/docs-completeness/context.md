# Contract: docs-completeness

## Objective
Fill in missing required documentation sections and fix inaccurate content identified in the docs-health report.

## Scope
- docs/DEVELOPER_GUIDELINES.md — add 4 missing sections
- docs/design.md — add 3 missing sections, remove stale class references
- README.md — add contributing section
- docs/knowledge_packs.md — add embeddings section
- docs/architecture.md — add missing LLM providers, fix BigQuery positioning

## Source Reports
- docs-health.a.md: design-missing-sections, devguidelines-missing-sections, readme-missing-contributing, knowledgepacks-missing-embeddings, design-stale-classes, arch-missing-providers, devguidelines-pytest-path, arch-bigquery-unimplemented

## Constraints
- All content added must be accurate to the current codebase state — read the relevant source files before writing
- Do NOT commit any changes
- Documentation must reflect the actual code, not aspirational states
