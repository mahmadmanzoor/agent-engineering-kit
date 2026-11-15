# Other ways to share a core

Whichever option you pick, the same five rules from the skill apply. The core decides and shells only wire. Nothing throws across the boundary. Tests run once and pass on both targets. Lint guards purity.

## Options, one at a time
- **Kotlin Multiplatform.** Choose it when Android is already native Kotlin and the iOS shell is Swift. Details: [kmp.md](kmp.md).
- **A Rust core,** reached through UniFFI, or through `swift-bridge` plus JNI. It suits heavy computation, cryptography, or a core that desktop or server code also uses. Return errors as values by mapping `Result`. A panic must never cross the FFI boundary, so wrap it with `catch_unwind`. Generate the bindings in CI.
- **A C++ core,** with Djinni-style bindings. Choose it when a C++ code base already exists. The rules do not change, and no exception may cross the C ABI.
- **A core in the app framework's own language,** meaning Dart in Flutter or TypeScript in React Native. It fits when the background logic can run inside the framework runtime, as a headless isolate or a JS task. This is the simplest route when the OS lets that runtime run in the background, because the native shells then only forward OS callbacks to it. Check background limits first. A killed process may not be able to restart the runtime.
- **Copies in each platform language.** Acceptable only for tiny, stable rules. Keep one shared set of test vectors, each a JSON input with the expected decision, and run it in both platforms' tests. That stops the copies from drifting.

## Record the choice
Write a decision: why you chose it, what it locks you into, and when to revisit it.
