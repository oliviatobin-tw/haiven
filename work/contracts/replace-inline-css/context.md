# Contract: replace-inline-css

## Objective
Replace inline CSS (style={{...}}) with Tailwind CSS classes across 27 files in the ui-components zone. CHARTER.yaml requires Tailwind exclusively.

## Scope
All 27 files with style={{...}} usage, tackled in order of severity.

## Source Reports
- ui-components-code-quality.a.md: css-01, css-02 (27 files, 118+ occurrences)

## Constraints
- Replace inline styles with equivalent Tailwind classes — do NOT change layout or visual appearance
- Run cd ui && yarn test after each file batch
- Commit per-file or per-batch to keep PRs reviewable
- If a style has no Tailwind equivalent, use a Tailwind arbitrary value: e.g. style={{width: "37px"}} -> className="w-[37px]"
- Most severe offenders first: api-keys.js (28), _navigation_items.js (13), _company_canvas.js (11)
