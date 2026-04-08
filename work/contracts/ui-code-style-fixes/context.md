# Contract: ui-code-style-fixes

## Objective
Fix small code style violations in the ui-components zone: JSDoc comments, file naming conventions, and utils directory naming consistency.

## Scope
- ui/src/app/_enrich_card.js — remove JSDoc comment
- ui/src/app/utils/_aggregate_token_usage.js — remove JSDoc block
- ui/src/app/utils/tokenUtils.js — remove JSDoc block
- ui/src/app/feature_toggle.js — rename to _feature_toggle.js and update imports
- ui/src/app/utils/promptDownloadUtils.js, rulesDownloadUtils.js, tokenUtils.js — rename to _prefix convention

## Source Reports
- ui-components-code-quality.a.md: jsdoc-01, jsdoc-02, jsdoc-03, naming-01, naming-02

## Constraints
- Do NOT touch inline CSS (separate contract)
- Run ui tests after each change: cd ui && yarn test
- Update all import references when renaming files
