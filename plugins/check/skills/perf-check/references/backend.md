# Backend: measuring speed

## Reading a slow query
Seed the test database with about ten times the data you expect in production, run `ANALYZE`, and only then judge the plan.

| Database | How to see the plan | What to watch |
|---|---|---|
| PostgreSQL | `EXPLAIN (ANALYZE, BUFFERS) <query>;` | `Seq Scan` on big tables, row estimates far from actual, sorts that spill to disk |
| MySQL | `EXPLAIN ANALYZE` | same |
| SQL Server | Actual execution plan | same |

Two extra rules:
- A table split by time (partitions, hypertables) needs a time filter in every query. Otherwise no partition is skipped.
- Any geometry column used in `WHERE` or `ST_DWithin` needs a GiST index.

## Finding which statements cost most
PostgreSQL has `pg_stat_statements`. It must be listed in `shared_preload_libraries = 'pg_stat_statements'`. Then:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
SELECT query, calls, round(mean_exec_time) AS avg_ms
FROM pg_stat_statements
ORDER BY avg_ms DESC
LIMIT 20;
```

Also log slow commands from inside the app. Hook the ORM, log anything over 100 ms, include the SQL text, and leave parameter values out of the log.

## Counting queries per request
Wire a counter into the data layer in the test, reset it, call the endpoint, assert the number. Run it with a one-item response and again with a many-item response. If the count grows with the items, you have an N+1.

| Stack | Where to hook |
|---|---|
| .NET, EF Core | A `DbCommandInterceptor` that counts `ReaderExecuting`. Call `Reset()` first. |
| Django | `django_assert_num_queries(n)` or `assertNumQueries(n)` |
| SQLAlchemy | `event.listen(engine, "before_cursor_execute", counter)` |
| Node (Prisma, Knex, TypeORM) | The query event or a logger, depending on the library |
| Spring, Hibernate | `hibernate.generate_statistics`, then `Statistics.getPrepareStatementCount()`. Or a datasource proxy. |

## Load scripts
A k6 script that holds 50 users on a notes listing. The run fails when p95 passes 200 ms or more than 0.1% of requests error:

```js
import http from "k6/http";
export const options = {
  vus: 50,
  duration: "4m",
  thresholds: { http_req_duration: ["p(95)<200"], http_req_failed: ["rate<0.001"] },
};
export default () => { http.get(`${__ENV.BASE_URL}/v1/notes?limit=50`); };
```

Run it: `k6 run -e BASE_URL=http://localhost:8080 perf/notes.js`. Gatling, Locust and Artillery do the same job.

## Benchmarking one function
- .NET: BenchmarkDotNet
- JVM: JMH
- Python: `pytest-benchmark`
- Node: `tinybench` or `mitata`
- Go: `testing.B`
