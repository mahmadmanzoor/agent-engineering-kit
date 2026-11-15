# React single-page apps and Next.js

This page maps the web rules onto React. Most web apps are client-rendered single-page apps (Vite plus a router). Content sites and mixed apps often use Next.js. Use the part that fits your project.

## 1. React single-page app (Vite, React Router, TanStack Query)

Where each piece lives:
- **Routes (thin):** route objects in `src/app/router.tsx`, lazy-loaded per feature with `lazy: () => import(...)`.
- **Feature folders:** `src/features/<feature>/{screens,components,hooks,data}`.
- **Screen:** `screens/<Screen>.tsx`. It renders state and calls actions from its hook.
- **View model:** `hooks/use<Screen>.ts`. It combines queries and mutations and exposes state and actions.
- **Repository:** `data/<thing>Repository.ts`. It wraps the generated client, maps models and problem codes, and exports query keys and `queryOptions`.
- **Generated client:** `src/api/generated/`, built from the contract with openapi-typescript and openapi-fetch, or with orval. If orval emits query hooks, keep them inside `data/`. Regenerate it. Never edit it.
- **Server-state cache:** TanStack Query with a single `QueryClient`. Keys are per resource, such as `['orders', id]`. Mutations call `invalidateQueries`. Turn `retry` off for 4xx.
- **Shared code:** `src/shared/{components,lib}`. Add an import rule, using eslint `no-restricted-imports` or dependency-cruiser, so it can never import `src/features/*`.
- **Copy:** `src/i18n/<locale>.ts` typed against the source locale, or use react-i18next or FormatJS.
- **Tokens:** custom properties in `src/styles/tokens.css`. A Tailwind theme may read them.
- **Config:** `import.meta.env.VITE_*`, parsed once at start with a schema (zod). Put no secret there, because the whole bundle is public.

### Working rules
- **Forms:** React Hook Form, validated by a zod schema that takes its limits from the contract. When the server refuses, feed the problem's `errors` into `setError(field)`.
- **Auth:** the server issues an httpOnly, Secure, SameSite cookie and the client sends `credentials: 'include'`.
  - CSRF: send a double-submit token header, or pair SameSite=Strict with an origin check made by the server.
  - One fetch middleware owns the status codes. It redirects a 401 to sign-in. For 403 and 404 it raises a typed error, which the screen turns into a state.
- **Errors:** the repository throws a typed `ApiProblem { code, fields? }`. A screen picks its message by switching on `code`.
- **Optimistic updates:** `onMutate` with rollback, for reversible actions only.
- **Accessibility:** run `eslint-plugin-jsx-a11y`, and move focus when the route changes.

### Tests
- Unit and component: Vitest with React Testing Library. Query by role and name.
- HTTP: MSW at the network boundary, fed recorded responses. One set of handlers can serve both unit tests and the browser in development.
- End to end: Playwright with `@axe-core/playwright`, pointed at the output of `vite build && vite preview`. Either seed a test backend or replay recorded responses.
- Full run, in order: `npm run typecheck`, `npm run lint`, `npx vitest run`, `npm run build`, then `npx playwright test`.

## 2. Next.js (App Router)

Where each piece lives:
- **Routes (thin):** `app/[locale]/<route>/page.tsx` loads data and the dictionary, then renders one screen or composition.
- **Layout:** `app/[locale]/layout.tsx`. Fonts come from `next/font/local`, the root is `<html lang dir>`, and metadata comes from `generateMetadata`.
- **Sections and screens:** `components/sections/<Name>.tsx` for content, `features/<feature>/...` for apps. They are Server Components by default.
- **Client behaviour:** mark leaf components with `"use client"`. Never mark a section or a layout.
- **Data:** Server Components call the repository. Interactive client state uses TanStack Query. A Server Action counts as an edge: it validates input, makes a single use-case call to the API, and maps any errors.
- **Headers and CSP:** `headers()` in `next.config.js`, or middleware that sets a nonce for scripts Next.js injects itself.
- **Images:** `next/image` with `width`, `height`, `sizes` and `alt`.

### App Router defaults to know
- A component is a Server Component unless its file says `"use client"`. Pushing that boundary down to the leaves keeps client script small.
- In current versions, `fetch` responses and GET route handlers are not cached by default. Turn caching on deliberately and say so in the code.
- Reading request data (`cookies()`, `headers()`, `params`, `searchParams`) makes a route dynamic. Await them where the installed version requires it.
- A Server Action is a public POST endpoint. Check the session and validate input inside it, every time.
- On Vercel, functions run on the Node.js runtime by default, not Edge. Pick Edge for a route only with a stated reason, and confirm every import works there.

### Rules for this stack
- If the policy bans third-party requests, do not use `next/font/google` at runtime. Download the font and load it with `next/font/local`.
- Use `dangerouslySetInnerHTML` only for JSON-LD.
- End to end: Playwright against the app started with `next build && next start`. Check the build output with a script that scans `.next/` or `out/`.

## Self-check greps
Each should return nothing for new code.

```bash
# generated client imported outside the data layer
grep -rnE "from '.*api/generated" --include='*.ts*' src | grep -v '/data/'
# tokens kept where scripts can read them
grep -rnE 'localStorage.*[Tt]oken' src/
# hex colours outside the token file
grep -rnE '#[0-9a-fA-F]{3,6}\b' --include='*.tsx' --include='*.css' src | grep -v tokens.css
# raw HTML injection other than JSON-LD
grep -rn 'dangerouslySetInnerHTML' app components src 2>/dev/null | grep -v 'ld+json'
```
