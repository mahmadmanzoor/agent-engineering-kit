# JVM: Spring Boot (Java or Kotlin)

Use this page to arrange Spring code by server layer. Package by feature, then split into layers inside each feature.

## Where things go
Under `com.example.<app>.<area>`:

- `domain`: plain classes or data classes, value objects and rules. No Spring, no JPA.
- `application`: `<Area>Service` and ports as interfaces.
- `persistence`: JPA entities or jOOQ / Spring Data JDBC mappings, repositories and queries.
- `web`: controllers, request and response records, `<Area>Validation` and mappers.
- `adapters`: vendor implementations of ports.

Spring Modulith can verify the boundaries with `ApplicationModules.of(App.class).verify()`. Suppose the project puts JPA annotations directly on domain classes. Then write that down as a decision, and let the domain allowlist admit those persistence annotations only.

## Working rules
- **Controllers:** thin. Check the shape with `@Valid` on request records, or with a validator you write. Give one service method the caller's id and map what it returns. A single `@RestControllerAdvice` renders errors as `ProblemDetail`.
- **Results:** a sealed interface carrying `kind` and `code`. In Kotlin, do not call it `Result`, which clashes with `kotlin.Result`. Name it `Outcome<T>` or `<Area>Result`.
- **Reads:** project into interfaces or records. Avoid N+1 with `@EntityGraph` or `JOIN FETCH`. Switch off `spring.jpa.open-in-view`. Use keyset paging (`Window`, `ScrollPosition`).
- **Bulk:** `@Modifying @Query` skips the persistence context, so clear it afterwards. Use JDBC batch inserts.
- **Transactions:** put `@Transactional` on service methods only.
  - Lock with `@Lock(PESSIMISTIC_WRITE)` or `pg_advisory_xact_lock`. Use `@Version` for optimistic checks.
  - For work after commit, `@TransactionalEventListener(phase = AFTER_COMMIT)` works, but a crash right after commit loses the event. Route anything that cannot be lost through an outbox table.
  - Calling a `@Transactional` method from its own class skips the proxy and runs without a transaction. Go through a different bean.
- **Time:** inject `java.time.Clock`. Tests use `Clock.fixed(...)`.
- **Config:** bind with `@ConfigurationProperties` records marked `@Validated`, and avoid scattered `@Value`. Each kind of secret gets its own properties class.
- **Logging:** parameterised messages. Never call `toString()` on an entity that holds personal data.
- **Outbound calls:** `RestClient` or `WebClient` with timeouts. Resilience4j supplies retry and breaker for idempotent reads. A send gets a breaker and a timeout, and only the job retries it.
- **Jobs:** use `@Scheduled` plus ShedLock to run on one instance only, or use a queue. Each job makes one service call.
- **Uploads:** set `spring.servlet.multipart.max-file-size` and `max-request-size`. Stream to object storage. Never buffer a whole file.
- **Contract drift:** springdoc exposes `/v3/api-docs`. Add a test that downloads it and compares it with the contract file.

## Kotlin extras
- Apply `kotlin("plugin.spring")` (all-open). Kotlin classes are final by default, and final classes quietly defeat `@Transactional` and `@Cacheable`.
- Apply `kotlin("plugin.jpa")` (no-arg). JPA entities must not be data classes. Make them ordinary classes whose `equals` compares ids.
- Domain types may be data classes or value classes, as long as they carry no JPA annotations.
- Run detekt and ktlint with warnings as errors, and Konsist for architecture tests.
- Do not call blocking JDBC from coroutine code unless it runs on `Dispatchers.IO`.

## Testing and tooling
- **Integration:** JUnit 5 and AssertJ. Use `@SpringBootTest` with `MockMvc` or `WebTestClient`, and Testcontainers with `@ServiceConnection` for a real database.
- **Query counts:** `datasource-proxy` or Hibernate statistics, asserted per request.
- **Architecture:** ArchUnit `layeredArchitecture()`, Konsist for Kotlin, Modulith `verify`.
- **Migrations:** Flyway (`V<n>__<name>.sql`) or Liquibase.
  - Flyway has no generator, so you write the SQL yourself. A test should run each script on a Testcontainers database, and you should read it for locks.
  - Undo needs the paid edition. Plan on rolling forward: a later migration repairs an earlier one.
  - A concurrent index needs `executeInTransaction=false`.
- **Full check:** `./gradlew check`, or `./mvnw verify` on Maven.

## Self-check greps
Each should return nothing for new code.

```bash
# repositories reached from the web layer
grep -rln 'Repository' --include='*.java' --include='*.kt' src/main | grep '/web/'
# clock reads that skip the injected Clock
grep -rnE 'LocalDateTime\.now\(\)|Instant\.now\(\)' src/main | grep -v Clock
# scattered @Value
grep -rn '@Value(' src/main
# catch-all handlers
grep -rnE 'catch \((e: )?Exception' src/main/
```
