---
name: web-rules
description: "Rules for laying out and writing web front-end code, for content sites (marketing, docs) and web apps (dashboards, signed-in tools). Covers thin routes, one layout, design tokens, copy dictionaries, no inline scripts, no third-party requests, accessibility, performance budgets, app layers, a server-state cache, forms, cookie sessions and tests that run on the built output. Use for any web UI code you write or review. Say: '/web-rules', 'design tokens', 'data fetching', 'web rules', 'dashboard structure', 'inline script', 'third-party script', 'where does this go in the front end'."
argument-hint: "[a web change, a file to place, or a diff]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Web rules

Apply the web front-end rules to `$ARGUMENTS`, which may be a change, a file to place or a diff. With no argument, use the change in hand.

**Run on:** opus at medium. Placement and security calls take judgment.

## Use it when
- You write or review web UI code and need to know where it belongs and which rules bind it.
- You are choosing between the content-site pattern and the web-app pattern.

**Not for:** building a single page (`add-page`), building a single app screen (`build-screen`), or the general placement rules (`code-placement`, ship plugin).

## Before you start
Read `AGENTS.md`, `CLAUDE.md` and the web folder's README. Find:
- the framework, the rendering mode (static, server-rendered, single-page, mixed), and the commands for lint, type-check, unit tests, build and e2e;
- the design source and the token source, which a mobile app may share;
- the copy dictionaries, the CSP and header config, and (for apps) the generated API client;
- the build-output checks.

Then choose a stack note: [references/react.md](references/react.md) or [references/astro.md](references/astro.md). If neither fits, map the rules onto the framework's own habits and say so. The project's own rules win. Missing a fact? Ask once and offer to write it into `AGENTS.md`.

## Steps
1. **Name the kind.** It is a content site, a web app, or both in one repo. Each part follows its own section below.
   **Stop if:** you cannot say which folder each part goes in and which commands prove it.
2. **Apply the shared rules** to every kind of web code. Where things live:
   - **Routes** sit in the framework's route folder. They stay thin: pick the locale and data, render one composition. No layout, copy or business rules.
   - **Layout** is one base layout holding the document head, CSP, fonts, header, footer, `lang` and `dir`.
   - **Shared components** live in a components folder that has import rules. They are small leaves with typed props and never import a feature.
   - **Copy** is one dictionary per locale. Components hold no literal user text. Plurals and placeholders go through the formatter. Other locales are type-checked against the source locale.
   - **Tokens** are one stylesheet of custom properties, mirrored from the single token source. A component never holds a hex literal.
   - **Static assets** sit in the framework's static folder. Fonts and media are self-hosted.
   - **Build guards** sit in a scripts folder that is not shipped. They check the built output.

   Then these cross-cutting rules:
   - **Tokens and contrast:** add every new colour to the token source before use. If a brand colour is too light against white, treat it as decoration. Put text and icons on its darker variant.
   - **Scripts:** no inline scripts. Set a strict `script-src 'self'`. Nonces are allowed only for scripts the framework injects, and structured data is the one exception. Never loosen the CSP to make code run.
   - **Third parties:** no third-party requests by default (CDN fonts, analytics, embeds, pixels). Each needs a decision record (`decision`, kit plugin) and a privacy note.
   - **Images:** use the image pipeline, with `width`, `height` and `alt` (`alt=""` when decorative), sized for the slot.
   - **Security headers:** set CSP, Referrer-Policy, Permissions-Policy, X-Content-Type-Options and HSTS once, and check them on the built output.
   - **Accessibility:** a single `<h1>`, headings in order, landmarks, real links and buttons, keyboard reach with visible focus, targets of at least 44 px, colour never the sole signal, logical CSS properties for right-to-left, and respect for reduced motion.
   - **Performance:** the project states a budget (script bytes, CSS bytes, a lab score, Core Web Vitals). A change that raises it says by how much.
   **Stop if:** the change needs a hex literal, an inline script, a third-party request or a weaker CSP.
3. **Apply the content-site rules.**
   - Each page has one composition component that holds section order and page data. Each section is one file. A new section is one new file and one line in the composition.
   - Ship no client script by default. Reach for HTML that needs none: `<details>`, `popover`, `:hover` paired with `:focus-visible`, CSS motion.
   - If script is unavoidable, use one bundled entry that calls `init*()` functions. Find elements through `data-*` hooks. Pass server values in `data-*` attributes, never as globals.
   - Adding a client framework runtime to a content site calls for a decision record that states what it costs in size.
   - Claims must match what the product does. Mark anything unbuilt as planned.
4. **Apply the web-app rules.** These are the same layers as a mobile app's (`app-rules`, mobile plugin), and they follow the server's error contract (`add-endpoint`, server plugin).

   - **Screen** (route component and its parts): handles layout, copy and states, and forwards user actions. It must not call the API client, hold business rules, or build messages from status codes.
   - **View model** (screen hooks): holds screen state, exposes actions as functions and combines repositories. It must not touch the DOM or import the generated client.
   - **Repository** (data module): owns one kind of data. It fetches, caches, invalidates, maps API models to app models and maps problem codes to typed errors. It must not hand generated API types to screens.
   - **Generated API client:** produced from the contract. Nobody edits it by hand, and nothing outside the data layer imports it.

   Further app rules:
   - **Server state** lives in one cache layer, keyed per resource. A write invalidates or updates the keys it affects. Do not copy server data into component state.
   - **Forms** copy the server's limits from the contract for instant feedback. They still handle the server's refusal (problem code and field names) and show it on the field.
   - **Session** lives in an httpOnly, Secure, SameSite cookie. No tokens in local storage. Writes that rely on the cookie need CSRF protection.
   - **401, 403 and 404** are handled in one place. 401 signs the user in again. 403 explains and hides the action. 404 means gone or no longer yours, so a member removed mid-session lands on a safe screen and learns nothing about the resource.
   - **Errors** key on stable problem codes, never titles or messages. An unknown code gets a generic, honest message and is reported.
   - **Optimistic updates** are for reversible, low-stakes actions only. Payments, and anything on the project's safety list, show the real result.
   - **States:** build every one per screen: loading, empty, error, retrying, forbidden, success. Long lists use the API's cursor.
   - **Config** comes from build-time environment variables, validated at start. No secret goes in the client bundle.
   **Stop if:** a screen imports the generated client, or a token sits where scripts can read it.
5. **Check the tests.** Write the test first (`test-first`, check plugin).
   - Content sites: e2e against the built site (each section in each locale, controls by keyboard, right-to-left) plus build-output checks.
   - Apps: component tests per state, with HTTP mocked at the network boundary using recorded responses. Repository tests on the same responses. E2E for critical journeys on a production build, against a seeded or recorded backend.
   - Run in this order: lint and type-check, unit and component, build with the output guard, e2e.

## Done when
- [ ] You named the kind and followed its section.
- [ ] Routes are thin and components typed. Text comes from the dictionary and styling from tokens.
- [ ] The build has no inline script and no third-party request. The CSP is unchanged and the headers are verified.
- [ ] Apps: screens do not import the generated client, errors key on codes, one place handles 401/403/404, the session is a cookie with CSRF protection, and every state exists.
- [ ] Content sites: script appears only where needed, through `init*()` and `data-*`.
- [ ] Accessibility basics hold, and the budget impact is stated.
- [ ] Tests sit at the right level, and the commands pass (output shown).

## Never
- Never introduce tracking or a third-party request unless a decision record exists and the user agrees.
- Never keep session tokens where scripts can read them.
- Never weaken the CSP, or hide an error, to get a change through.
- Never override the project's own names and paths because another project does it differently.

## Next
- **Comes from:** `add-page`, `build-screen` (web), `build` (ship), `review-code` (check)
- **Leads to:** `a11y-audit`, `perf-check`, `security-review` (check); `decision` (kit) for a new framework or third party
