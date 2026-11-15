# Kotlin Multiplatform core, Swift shell

## Folder layout
`shared/` is a separate Gradle build that holds the core. Put your package path where `<pkg>` appears.

- `shared/build.gradle.kts` declares three targets: an Android library, `iosArm64` and `iosSimulatorArm64`.
- `shared/src/commonMain/kotlin/<pkg>/core/` holds every rule.
- `shared/src/commonTest/kotlin/<pkg>/core/` tests those rules with `kotlin.test` and fakes for the core's interfaces.
- `shared/src/androidMain/` and `shared/src/iosMain/` contain nothing but `expect/actual` primitives, for instance a re-entrant lock.
- `shared/src/androidHostTest/` is for JVM-only tests that need real threads.
- `android/app/src/main/kotlin/<pkg>/` holds the Android adapters, the shell and the bridge plugin.
- `ios/Runner/<Feature>/` holds the Swift adapters and shell. It does `import SharedCore`.

To link the framework into Xcode, add a Run Script build phase running `./gradlew :shared:embedAndSignAppleFrameworkForXcode` (direct integration). An XCFramework also works.

## What `commonMain` may contain
- **Allowed:** pure functions, small classes, the `kotlinx.serialization` JSON tree API (no compiler plugin, so the build stays simple), `kotlin.time.Instant` for ISO timestamps, and `kotlin.concurrent.Volatile`.
- **Banned, enforced by lint with no baseline:** `java.*`, `android.*`, `platform.*`, `kotlinx.coroutines`, `Clock.System`, `println` and `print`, files, SQLite, Keystore and Keychain, and schedulers. For logging, accept a parameter `log: (String) -> Unit`.

## Crossing into Swift (Objective-C export)
- **Throw nothing into Swift.** An uncaught Kotlin exception brings the app down once it reaches Swift. Interfaces answer with `null` or `false`. Each entry point called from Swift traps every error and returns an outcome. `@Throws` is no escape hatch, so leave it out.
- **Enum entries use `UPPER_SNAKE_CASE`.** `NOT_ALLOWED` shows up as `.notAllowed`. `NotAllowed` would show up as `.notallowed`. Add a `default` branch to any Swift `switch` on a Kotlin enum.
- **No `Pair` or `Triple`, and no reliance on default arguments.** Swift sees every parameter, so give it a small `data class` instead. Constants live in a `companion object`, and Swift reads them as `Uploader.companion.BATCH_SIZE`.
- **Numbers.** A Kotlin `Int` is an `Int32` in Swift. Nullable numbers, and lambdas that return `Boolean`, come across boxed as `KotlinLong?` and `KotlinBoolean`. Choose `Long` epoch milliseconds and `Double`. Gather every conversion in `CoreBridge.swift`.
- **Lambdas returning `Unit`** turn into plain Swift closures. For a parameter typed `(() -> Unit) -> Unit`, Swift receives a task whose result is `KotlinUnit`. Handle it like this: `{ task in queue.async { _ = task() } }`.
- **Protocol conformance** in Swift reads `final class NoteQueue: NSObject, QueueStore` and uses the exported labels.
- **Kotlin objects** appear in Swift as `Object.shared`.
- **Test names** in common code can be backticked sentences, but Kotlin/Native rejects the characters `, ( ) . : #`, so keep them out.

## Commands (change the names to fit)
- `./gradlew :shared:allTests` runs core tests on the JVM and in the iOS simulator.
- `./gradlew :shared:iosSimulatorArm64Test` runs the simulator target alone.
- `./gradlew :app:testDebugUnitTest` runs the Android glue tests.
- `xcodebuild test -scheme Runner -destination 'platform=iOS Simulator,name=iPhone 16'` runs the Swift side.
- `ktlint && swiftlint --strict` checks style.

## Lint checks worth writing
A shell script is enough for all three.
- **Core purity.** Each `commonMain` import must match `^import (kotlin|kotlinx)\.` and must not be `kotlinx.coroutines`. No `Clock.System`, no `println`.
- **Shells decide nothing.** Grep the Android and iOS glue for `== Problem.`, `!= .none` and `state ==`.
- **Size.** Production files have at most 320 lines (`wc -l`) and at most 3 top-level `class|object|interface|enum|struct|protocol` declarations. Skip `*.g.*` files.

## Sources
- Kotlin and Swift/Objective-C interoperability: https://kotlinlang.org/docs/native-objc-interop.html
- Direct integration with Xcode: https://kotlinlang.org/docs/multiplatform/multiplatform-direct-integration.html
- The Android Kotlin Multiplatform library plugin: https://developer.android.com/kotlin/multiplatform/plugin
- Functional core, imperative shell (Gary Bernhardt): https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell
