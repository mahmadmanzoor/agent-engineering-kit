# iOS with Swift

Examples use a notes app.

## Layer by layer
- **View.** A SwiftUI `View` struct that draws a state value. UIKit view controllers also work if you keep them thin.
- **View model.** A `final class` marked `@MainActor`, using `@Observable` or `ObservableObject`. It holds an immutable state struct and one method per action. Keep `UIKit` and `SwiftUI` imports out of it when you can.
- **Domain.** One Swift package target. It holds structs, `enum` results with associated values, and the repository `protocol`s.
- **Repository.** A `final class` that conforms to the domain protocol. It publishes through `AsyncStream` or Combine. It converts `Codable` DTOs and stored models into domain models.
- **Coordinator.** Either an `actor`, or a `final class` that owns a `Task` and cancels it on sign-out.
- **Service.** A `URLSession` client (or a generated OpenAPI client), a storage wrapper, or a wrapper over a platform API.

## Wiring
- **Modules:** one Swift Package Manager target per feature, and a `Shared` target. Shared may not depend on any feature.
- **Strings:** String Catalogs (`.xcstrings`), including plural variants.
- **Theme:** a single `Theme` type, or colour sets in the asset catalog. Add a SwiftLint custom rule that rejects `Color(red:...)` literals.
- **Local database:** SwiftData, Core Data or GRDB, with versioned migrations. Add a test that opens a store the previous release wrote.

## Code rules
- Use `async`/`await`. Mark UI state `@MainActor`. Use `[weak self]` in closures that live a long time. Do not mix dispatch queues and actors inside one type.
- Outside tests, write no `try!` and no force unwraps. Catch specific errors with `do/catch`.
- Default to `final class`. Name things as the Swift API Design Guidelines say.

## Enforcement
- Target dependencies in the package manifest already encode the layer rules.
- For finer rules, run a script over the `import` lines.
- Run SwiftLint in CI with an empty baseline.

## Speed
- Keep `body` cheap.
- Use `LazyVStack` or `List` with stable ids.
- Profile with Instruments (Time Profiler, SwiftUI, Hangs), on a real device, in a Release build.
