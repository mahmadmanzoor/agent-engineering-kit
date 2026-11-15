# JVM testing notes (Java and Kotlin)

## Running tests
- One test, Gradle: `./gradlew test --tests "notes.TitleLimitTest.accepts at most 80 characters"`
- One test, Maven: `mvn -Dtest=TitleLimitTest#acceptsAtMost80 test`
- One module: `./gradlew :api:test`
- Everything: `./gradlew test`

## Tools
- **Framework:** JUnit 5. In Kotlin, kotlin.test or Kotest on top of JUnit.
- **Clock:** inject `java.time.Clock`. Tests use `Clock.fixed(...)` or a clock they can move.
- **Parameterised tests:** `@ParameterizedTest` with `@CsvSource`.
- **Architecture rules:** ArchUnit, or Konsist for Kotlin.
- **Android unit tests:** plain Kotlin tests for logic. Robolectric only when the Android framework is truly needed.
- **Mock libraries:** Mockito or MockK, for true boundaries only (vendors, the OS). Never for your own services.

## Integration tests
- **Spring:** `@SpringBootTest(webEnvironment = RANDOM_PORT)` with `WebTestClient` or `MockMvc`. **Ktor:** `testApplication`.
- **Database:** Testcontainers running the production engine, with Flyway or Liquibase migrations applied for each test class.
- **Spring Boot 3.1 and later:** declare the container as a bean marked `@ServiceConnection`, so the datasource configures itself. A static `@Container` field with `@ServiceConnection` also works.

```kotlin
@TestConfiguration(proxyBeanMethods = false)
class DbContainer {
    @Bean
    @ServiceConnection
    fun database() = PostgreSQLContainer("postgres:17-alpine")
}

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Import(DbContainer::class)
class ListNotesTest(@Autowired private val web: WebTestClient) {
    @Test
    fun `a stranger asking for a shared notebook gets 404`() {
        web.get().uri("/v1/notebooks/${UUID.randomUUID()}/notes")
            .headers { it.setBearerAuth(tokenFor("stranger")) }
            .exchange()
            .expectStatus().isNotFound
    }
}
```

## Parameterised sample
```kotlin
class TitleLimitTest {
    @ParameterizedTest
    @CsvSource("80,true", "81,false")
    fun `title allows at most 80 characters`(length: Int, expected: Boolean) {
        assertEquals(expected, Note.titleFits("a".repeat(length)))
    }
}
```

## Kotlin details
- Write `App::class.java`, `catch (e: IOException)` and `assertThrows<NotebookFull> { ... }`. Sources sit under `src/main/kotlin` and `src/test/kotlin`.
- Kotlin/Native rejects some characters in backticked test names: `,` `(` `)` `.` `:` `#`. Keep names plain if tests run on native targets.
