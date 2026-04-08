## Objective
Investigate the health of the `ui-components` zone — React/Next.js components, pages, and hooks.

## Scope
Files in `ui/src/app/**`, `ui/src/pages/**`, `ui/src/hooks/**` (63 files).
Components follow the `_component_name.js` naming convention.

## Key Questions
- Do components follow the `_component_name.js` naming convention?
- Are components functional (hooks-based), not class-based?
- Is the Next.js client-only constraint respected (no server-side features used)?
- Are Remix icons used exclusively (no other icon library imports)?
- Are there inline CSS styles (should use Tailwind)?
- Are there files over 300 lines?
- Is component responsibility well scoped, or are there "mega" components?

## Rules from CHARTER.yaml
- Allowed: functional components with hooks, Remix icons, Tailwind CSS, Ant Design, client-only mode, `_component_name.js` naming
- Forbidden: class-based components, inline CSS, server-side Next.js features, JSDoc comments, other icon libraries, jQuery
- Max file lines: 300, target test coverage: 70%

## Expected Output
An assertion-backed markdown report (.a.md) with evidence for each assertion.
Use the assertion-backed-markdown skill to produce the report.
