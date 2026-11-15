# Node.js with TypeScript (Express, Fastify, NestJS)

Use this page to lay out a TypeScript backend by the server layers. Compile with `strict: true`.

## Where things go
Organise by feature. Every area is a folder with five subfolders.

- `src/<area>/domain/`: entities, value objects and pure rules. It imports only other domain files.
- `src/<area>/application/`: `<area>.service.ts`, one method per use case, with ports as interfaces.
- `src/<area>/persistence/`: repositories over the ORM or query builder, mappings and queries.
- `src/<area>/http/`: routes or controllers, request and response schemas, validation and mappers.
- `src/<area>/adapters/`: vendor implementations of the ports.

Outside the areas:
- `src/shared/` is allowed only when its purpose and its import rule are written down.
- `src/workers/` holds thin job handlers (BullMQ or pg-boss).
- `src/main.ts` is the composition root.

On NestJS, each area becomes a module with the same folders. Keep HTTP types like `HttpException` out of the providers in `application/`. A controller or an exception filter is the only place that turns a result into an exception.

## Working rules
- **Handlers:** parse the input with a schema (zod, or TypeBox on Fastify), hand `req.user.id` to one service, and turn the result into a problem response. Cover the 500 path with one shared error handler.
- **Results:** model them as a discriminated union (`{ ok: true, value }` or `{ ok: false, error }`). The error carries a `kind` and a `code`. Consume it with an exhaustive `switch` and a `never` check in the default branch.
- **ORM (Prisma, Drizzle, Kysely, TypeORM):** fetch only the fields you use. Take care with `include` and with loops that call `findUnique`, which are the usual N+1 sources. Bulk work goes through `updateMany` and `createMany`.
- **Transactions:** `prisma.$transaction(async (tx) => ...)`, or `transaction().execute` in Kysely. Take advisory locks through raw SQL. Notify once the transaction has resolved.
- **Time:** pass in a `Clock` of the shape `{ now(): Date }`, and keep `Date.now()` out of rules.
- **Config:** build one typed object and validate it with zod when the process starts. If validation fails, exit. Nothing else reads `process.env`.
- **Async:** await or handle every promise (`no-floating-promises`). Pass an `AbortSignal` to fetch and database calls.
- **Logging:** pino, with `redact` paths for tokens, emails and phone numbers.
- **Outbound calls:** `fetch` or `undici` with `AbortSignal.timeout`. Use `cockatiel` or `opossum` for retry and breaker, on idempotent reads only. The job queue retries sends, with an idempotency key.
- **Dependency injection:** inject through constructors, using a light container (tsyringe, awilix) or NestJS providers. Only objects that hold a transaction get request scope.

## Testing and tooling
- **Runner:** Vitest or Jest. Test HTTP with `supertest` or Fastify `inject`, and use a real database (testcontainers, or the one in the compose file).
- **Query counts:** count statements per request with Prisma `$on('query')` or a Kysely log hook.
- **Architecture:** dependency-cruiser rules, ESLint `no-restricted-imports`, `eslint-plugin-boundaries`.
- **Migrations:** pick Prisma Migrate (create with `migrate dev --create-only`, then read `migration.sql`), Drizzle Kit, Knex or node-pg-migrate. Concurrent index builds need a non-transactional migration.
- **Full check:** `npm run typecheck && npm run lint && npm test`.

## Self-check greps
Each should return nothing for new code.

```bash
# data access inside the http layer
grep -rnE 'prisma\.|db\.' src/*/http
# clock reads in rules and services
grep -rnE 'Date\.now\(\)|new Date\(\)' src/*/domain src/*/application
# env reads outside config
grep -rn 'process\.env' src/ | grep -v 'config'
# swallowed errors
grep -rnE 'catch *\(\w*\) *\{ *\}' src
```
