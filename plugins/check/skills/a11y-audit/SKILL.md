---
name: a11y-audit
description: "Check a UI change for WCAG 2.2 AA problems on web and mobile. Adds automated checks to the tests (names, target size, contrast, 200% text), works through a manual checklist, then runs the flow with a screen reader on a real device. Use for UI-heavy work and before a release. Say: '/check:a11y-audit', 'a11y review', 'is this accessible', 'screen reader check', 'contrast', 'WCAG'."
argument-hint: "[screen, page, folder, PR or mockup]"
license: MIT
metadata:
  version: "1.0.0"
  model: sonnet
  effort: medium
---

# Accessibility audit

Audit `$ARGUMENTS`: a screen, page, feature folder, PR or design. With no argument, audit the UI files in the branch diff. Three people must get through every critical flow: one with large text, one using a screen reader, one in a hurry or under stress.

**Run on:** sonnet at medium. Mostly a checklist, run partly by scripts and partly by hand.

## Use it when
- A change is mostly UI, or a release is near.
**Not for:** building the screen (`/mobile:design-to-screen`, mobile; `/web:add-page`, web). General review (`/check:review-code`).

## Before you start
Read AGENTS.md or CLAUDE.md, then the design system: colour tokens, type scale, shared components, and any table of measured contrast. Look in the tests for helpers that already exist (guideline matchers, an "expect accessible" helper, automated scans). Pick the platform and open its reference: [web](references/web.md), [mobile](references/mobile.md), [flutter](references/flutter.md).

## Steps
1. **Put automated checks in the UI test.** Then a regression breaks the build, and nobody has to remember.
   - Each interactive element has an accessible name.
   - Minimum target size: 48x48 dp (Android), 44x44 pt (iOS), 24x24 CSS px (web; WCAG 2.2 minimum, 44 advised).
   - Text contrast 4.5:1, or 3:1 for large text. Icons, borders and focus rings need 3:1.
   - One test at 200% text scale: nothing overflows, no control is clipped, the key text still shows.
   **Stop if:** the checks are not part of the suite, or they fail.
2. **Walk the manual checklist.** Mark every item as a finding or a pass.
   - **Names.** Icon-only buttons carry a label taken from the localisation files. Rows and map pins announce what they are and what state they are in.
   - **Order.** A screen reader reads in the order the eye does. Decorative images and backgrounds are hidden from it.
   - **Meaning without colour.** Success, warning, error, offline and selected each add text or a distinct icon shape.
   - **Contrast.** Measure every new pair of text and background tokens. A pair that fails never carries text. A brand colour that fails against white is decoration only. If the project keeps a contrast test, add the pair to it.
   - **Targets.** Critical actions get big, forgiving targets with gaps between neighbours.
   - **Motion.** Pulses, spinners, parallax and autoplay all switch off once the OS asks for less motion.
   - **Scaling.** Layout holds at 200% text (WCAG 1.4.4). On web it also reflows at 320 CSS px (1.4.10).
   - **Time limits.** A timed flow says how long is left, and the user can extend or cancel it without a precise gesture.
   - **Sound and touch feedback.** No critical event is signalled by sound or vibration alone.
   - **Right-to-left.** Layout mirrors through logical properties. Icons that point somewhere flip.
   - **Errors.** The message says what went wrong and what to do next. It is announced through a live region or an announcement call.
   - **Focus.** Keyboard and switch access reach every control. Focus is visible and never trapped. A dialog takes focus on open and gives it back on close.
   - **Sign-in.** No puzzle or memory test without an alternative (WCAG 3.3.8). Pasting into code and password fields works.
3. **Try it on a device.** For UI-heavy work, run the whole flow with the platform screen reader: TalkBack, VoiceOver, or a desktop reader on web. Set the system font to its largest. Do the main action, then cancel it. Write down in the PR what you tested.
   **Stop if:** the main action fails with the screen reader on, or at the largest font.
4. **Report.** For each finding give the severity, `file:line`, the WCAG criterion and the fix. List the checks that passed. Rate a finding `critical` when a critical action cannot be done by screen reader, keyboard or at large text. The new automated checks ship with the fix.

## Done when
- [ ] The automated checks run in the suite and pass (command and result line).
- [ ] Every checklist item is a finding or a pass.
- [ ] The device pass is noted in the PR, or marked not done with the reason.
- [ ] Each finding names a criterion, a location and a fix.

## Never
- Fix a warning or error colour by washing it out until it no longer stands out. Choose a darker token.
- Hard-code accessibility labels. They live in the localisation files like all other strings.
- Merge an accessibility regression on a critical flow.

## Next
- **Comes from:** `/check:review-code` (dimension 8), `/mobile:design-to-screen` (mobile), `/web:add-page` (web), `/ship:release` (ship)
- **Leads to:** `/ship:file-bug` (ship) for findings outside the change. `/mobile:device-test` (mobile) for the device pass.
