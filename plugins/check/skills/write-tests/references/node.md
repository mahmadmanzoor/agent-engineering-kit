# Node and TypeScript testing notes

## Running tests
- One test: `npx vitest run src/notes.test.ts -t "accepts at most 80 characters"`. Jest takes the same `-t` flag.
- One folder: `npx vitest run src/notes`
- Everything: `npm test`

## Tools
- **Framework:** Vitest or Jest, whichever the project uses. `node:test` fits small packages.
- **Clock:** pass in a `clock` or a `now()` function. Reach for fake timers (`vi.useFakeTimers()` or `jest.useFakeTimers()`) only when you test timer scheduling.
- **Parameterised tests:** `it.each` or `test.each`.
- **Vendors:** recording fakes behind ports. For recorded HTTP use `msw` or `nock`.
- **UI:** Testing Library for components, Playwright for end to end. Prefer `getByRole` with the accessible name over test ids. It checks accessibility as well.
- **Architecture rules:** dependency-cruiser, or the ESLint rule `no-restricted-imports`.

## Integration tests
- Call the app object with `supertest` (Express, Fastify), or build a Nest `createTestingModule`.
- Use the real database engine, from a container or a local service. Migrate a fresh schema per file and truncate tables between tests.

## UI tests against an API
`msw` intercepts requests at the network layer, so the real fetching code (client, cache, retries) still runs. Build handlers from recorded or contract-shaped responses. Include error replies (401, 403, 404 with problem codes) and delayed replies, so loading states get tested too.

```ts
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";

// the same server object serves every test in the file
const server = setupServer(
  http.get("/api/notes/:id", () => {
    const problem = { type: "about:blank", code: "note_not_found" };
    return HttpResponse.json(problem, { status: 404 });
  }),
);

beforeAll(() => {
  server.listen({ onUnhandledRequest: "error" }); // unmocked calls fail the test
});
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Parameterised sample
```ts
import { describe, it, expect } from "vitest";
import { titleFits } from "./notes";

describe("note title limit", () => {
  it.each([[80, true], [81, false]])("a %i-character title fits: %s", (length, fits) => {
    expect(titleFits("a".repeat(length))).toBe(fits);
  });
});
```
