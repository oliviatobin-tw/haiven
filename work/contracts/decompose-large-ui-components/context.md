# Contract: decompose-large-ui-components

## Objective
Decompose the largest UI component files (>300 lines) into smaller, focused components. This improves readability, testability, and maintainability.

## Scope
- ui/src/pages/_cards-chat.js (750 lines) — highest priority
- ui/src/pages/api-keys.js (541 lines) — if inline CSS replacement didn't already shrink it enough
- ui/src/pages/creative-matrix.js (475 lines)
- ui/src/pages/scenarios.js (428 lines)
- ui/src/app/_prompt_chat.js (392 lines)
- ui/src/pages/_company_canvas.js (354 lines)
- ui/src/app/_chat.js (335 lines)
- ui/src/pages/index.js (332 lines)

## Source Reports
- ui-components-code-quality.a.md: size-01, size-02, size-03

## Constraints
- This contract depends on replace-inline-css being complete first (avoids conflicts)
- Each decomposition must not change any visible behavior
- New component files must follow the _component_name.js naming convention
- Run cd ui && yarn test after each decomposition
