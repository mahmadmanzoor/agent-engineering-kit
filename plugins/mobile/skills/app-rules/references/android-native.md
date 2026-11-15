# Android with Kotlin

The layers match Google's own app architecture advice: a UI layer, a data layer, and an optional domain layer between them. Examples below use a notes app.

## Layer by layer
- **View.** Compose screens that take a state value and an `onAction` callback, such as `NotesScreen(state, onAction)`. Keep them stateless where you can. Fragments and Views also work.
- **View model.** A `androidx.lifecycle.ViewModel` that exposes `StateFlow<UiState>` and one method per action. `UiState` is an immutable `data class` or a `sealed interface`. The class never imports `Context` or Compose.
- **Domain.** A plain Kotlin module with `data class` models, `sealed interface` results and the repository interfaces.
- **Repository.** Implements the domain interface and returns `Flow`. It converts Retrofit or Ktor DTOs and Room entities into domain models.
- **Coordinator.** Owns a `CoroutineScope` built from a `SupervisorJob` and an injected dispatcher. Start it from `Application` or from a worker.
- **Service.** A Retrofit or Ktor client, a Room DAO, or a wrapper over a platform API.

## Wiring
- **DI:** Hilt or Koin. Tests swap the bindings.
- **Modules:** one Gradle module per feature (`:feature:notes`) and one shared module (`:core:<name>`). `:core` must never depend on `:feature`.
- **Strings:** `res/values/strings.xml`, using `plurals` for counts.
- **Theme:** a Material 3 `ColorScheme` plus any custom tokens, all in one theme file.
- **Local database:** Room with `@Database(version = N)`. Cover migrations with `AutoMigration` or `MigrationTestHelper` tests.

## Code rules
- Read state in Compose with `collectAsStateWithLifecycle()`. Treat a one-off event as part of state. Do not fake it with `SharedFlow`.
- Never use `GlobalScope`, and never call `runBlocking` on the main thread. Inject dispatchers so tests can run on `StandardTestDispatcher`.
- Write no `!!` in new code. Catch named types such as `IOException` or `SecurityException`.

## Enforcement
- Write Konsist or ArchUnit tests for layer imports.
- Let Gradle module boundaries carry the coarse rules.
- Run `ktlint` and `detekt` in CI with an empty baseline.

## Speed
- Give Compose stable or immutable state classes. Use `remember` and `derivedStateOf`.
- Build lists with `LazyColumn` and a `key`.
- Do not read state high in the tree.
- Ship Baseline Profiles to speed startup, and use Macrobenchmark to time frames.
