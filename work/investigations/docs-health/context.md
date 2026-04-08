## Objective
Investigate whether the documentation defined in CHARTER.yaml exists, is structurally complete,
and is up to date with the codebase.

## Scope
Docs defined in CHARTER.yaml:
- README.md (sections: intro, quickstart, deployment, knowledge packs, contributing)
- CONTRIBUTING.md
- docs/architecture.md (sections: deployment architecture, runtime architecture)
- docs/design.md (sections: component design, python components, react components)
- docs/DEVELOPER_GUIDELINES.md (sections: getting started, running the app, running tests, code standards, git workflow)
- docs/knowledge_packs.md (sections: structure, creating a pack, embeddings)
- docs/why.md

References: .junie/guidelines.md, docs/DEVELOPER_GUIDELINES.md

## Key Questions
- Do all required docs exist?
- Do they contain all required sections from CHARTER.yaml?
- Is the content accurate with respect to the current codebase (commands, paths, versions)?
- Are there broken internal links or references to files that no longer exist?

## Expected Output
An assertion-backed markdown report (.a.md) with evidence for each assertion.
Use the assertion-backed-markdown skill to produce the report.
