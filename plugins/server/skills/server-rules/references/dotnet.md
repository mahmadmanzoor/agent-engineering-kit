# .NET: ASP.NET Core and EF Core

Use this page to place server layers in a .NET solution. If the project already has a layout, follow that instead.

## Where things go
- **Domain:** a `<App>.Domain` library with no packages beyond the base library.
- **Persistence:** `<App>.Persistence` holds the `DbContext`, one `IEntityTypeConfiguration<T>` per entity, `Queries/` for `IQueryable` extensions, `Locks/`, and `Migrations/`.
- **Application:** `<App>.Application/<Area>/<Area>Service.cs`, with ports in `Abstractions/`.
- **Edge:** `<App>.Api`. Minimal APIs with one `MapGroup` per area, request and response records, `<Area>Validation.cs`, mappers, and `Program.cs` as the composition root.
- **Workers:** `<App>.Workers` on Hangfire or Quartz. Use a `BackgroundService` until a job host exists.

## Working rules
- **DbContext:** scoped to one request or job, and not thread-safe. Never run two queries on it at the same time. Reads use `AsNoTracking()`.
- **Async:** async from top to bottom. Give every database and HTTP call a `CancellationToken`. No `.Result`, `.Wait()` or `async void`.
- **Realtime hubs:** keep them thin, like any edge. The server decides which groups a connection joins, from membership. A group name sent by the client is never trusted.
- **Handlers:** return `TypedResults`. Put `RequireAuthorization()` on the group and `.WithName("<operationId>")` so it matches the contract.
- **Errors:** `Result<T>` with `Error(Kind, Code, Title)`, mapped to `TypedResults.Problem(...)`. Cover the 500 path with `UseExceptionHandler` and `AddProblemDetails()`.
- **Validation:** write `<Area>Validation` by hand and return `TypedResults.ValidationProblem`. Annotations on request records are ignored unless you register validation for them. Decide once and write it down.
- **Reads and bulk:** pair `AsNoTracking()` with `Select`. Change many rows with `ExecuteUpdateAsync` or `ExecuteDeleteAsync`. If a query has several `Include` calls, add `AsSplitQuery()`.
- **Transactions and locks:** `BeginTransactionAsync(ct)`; `pg_advisory_xact_lock`. For optimistic concurrency, map `xmin` with `.IsRowVersion()` and turn `DbUpdateConcurrencyException` into a conflict.
- **Time:** inject `TimeProvider`. Tests swap in `FakeTimeProvider`.
- **Options:** `AddOptions<T>().BindConfiguration(...).ValidateDataAnnotations().ValidateOnStart()`. Constructors never take `IConfiguration`.
- **Logging:** `ILogger<T>` with message templates. `{@Object}` serialises the whole object, so keep it away from personal data.
- **Outbound calls:** `IHttpClientFactory` with `AddStandardResilienceHandler`, retries off for unsafe methods. A send gets only a breaker and a timeout.
- **Dependency injection:** register anything holding a `DbContext` with `AddScoped`, and stateless adapters with `AddSingleton`. A singleton that needs a scope takes an `IServiceScopeFactory`. Each project exposes one `Add<Project>(this IServiceCollection)` method.
- **Analyzers:** set `AnalysisLevel` to `latest-recommended` and turn on `TreatWarningsAsErrors` in `Directory.Build.props`. Suppress at the line, with a `Justification`.

## Testing and tooling
- **Integration tests:** xUnit with `WebApplicationFactory<Program>`, run against a real database from Testcontainers or the compose file. Give each test class its own fresh database.
- **Query counts:** a `DbCommandInterceptor` that counts commands for each request.
- **Architecture:** run ArchUnitNET or NetArchTest against the compiled assemblies.
- **Migrations:** `dotnet ef migrations add <Name> --project src/<App>.Persistence`. To read the SQL, run `dotnet ef migrations script <Prev> <Name>`. Building an index concurrently requires `suppressTransaction: true`.
- **Full check:** `dotnet format --verify-no-changes && dotnet build -warnaserror && dotnet test` (all three must pass).

## Self-check greps
Each should return nothing for new code.

```bash
# data access in the API project (health checks excepted)
grep -rlE 'DbContext|BeginTransaction' src/*.Api --include='*.cs' | grep -v Health/
# direct clock reads outside migrations
grep -rnE 'DateTime(Offset)?\.(UtcNow|Now)' --include='*.cs' src | grep -v Migrations
# raw configuration in constructors
grep -rn 'IConfiguration ' --include='*.cs' src | grep -vE 'Program.cs|ServiceCollectionExtensions'
# catch-all handlers
grep -rnE 'catch *\(Exception' --include='*.cs' src
```
