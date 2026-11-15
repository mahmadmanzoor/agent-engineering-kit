# Web accessibility: tooling and markup rules

## Automated tools
- **axe-core in end-to-end tests.** With Playwright: `new AxeBuilder({ page }).analyze()`, then assert that `violations` is empty. For component tests use `jest-axe` or `vitest-axe`.
- **Role-based queries.** Testing Library's `getByRole('button', { name: 'Save note' })` doubles as a check. If the query cannot find the element, a screen reader cannot either.
- **Lighthouse in CI** (`lhci autorun`). Its score covers only part of WCAG. Keep the manual checks.

## Markup rules
| Topic | Rule |
|---|---|
| Structure | One `<h1>` per page. Headings descend in order. Landmarks: `header`, `nav` (with `aria-label`), `main`, `footer`. |
| Controls | Use real `<a>` and `<button>`. Every input has a `<label for>`. |
| Images | Always set `alt`. Use `alt=""` for decoration. |
| Focus ring | `:focus-visible` outline at 3:1 against its background. Never `outline: none` without a replacement. |
| Focus containment | Use `inert` or a focus trap only while a modal is open. |
| Motion | Wrap every CSS and JS animation in `@media (prefers-reduced-motion: reduce)` handling. |
| Text sizing | Size in `rem`. No fixed heights on text boxes. Reflow at 320 px. |
| Direction | Set `dir` and `lang` on `<html>`. Prefer `margin-inline-start` and `inset-inline-end` over left and right. |

## Screen readers to try
NVDA or JAWS on Windows. VoiceOver on macOS and iOS. TalkBack with Chrome on Android.
