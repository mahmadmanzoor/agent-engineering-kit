# Flutter

How the layers land in a Flutter app, plus the rules that only apply here. Examples use a notes app.

## Where each layer lives
- **View.** A stateless or consumer widget at `features/notes/presentation/notes_screen.dart`. Break a screen into widget classes under `presentation/widgets/`. Do not write `Widget _buildX()` helper methods.
- **View model.** A Riverpod `Notifier` or `AsyncNotifier` in `notes_view_model.dart`. It imports neither `material.dart` nor `BuildContext`.
- **Domain.** The `domain/` folder holds immutable models (`final` fields with `==` and `copyWith`, or freezed), `sealed class` results, and repository contracts written as `abstract interface class`.
- **Repository.** `data/api_notes_repository.dart`. A top-level provider exposes it under the domain interface type.
- **Coordinator.** `data/sync_coordinator.dart` and similar. A provider that outlives the session starts it.
- **Service.** The generated OpenAPI client sits in `lib/api/`, Pigeon bindings in `lib/native/`, and plugin wrappers in `data/`.
- **Shared module.** `lib/shared/{domain,data,presentation}/`.
- **Feature handle.** `data/<feature>_providers.dart`, containing only lines like `export '...' show ...;`.
- **Strings.** ARB files, built with `flutter gen-l10n` and read through `AppLocalizations.of(context)`.
- **Theme.** One `theme.dart` with `AppColors` and the text styles. A test fails on `Color(0x...)` anywhere else.
- **Local database.** Drift. Tables and DAOs sit in a database service. Migrations are versioned and covered by `SchemaVerifier` tests.

## Riverpod rules
- Each provider is a top-level `final` with a unique name and the interface as its type. A `fake_*` file never declares one.
- Call `ref.watch` in `build` and `ref.read` in callbacks. Narrow a rebuild with `ref.watch(p.select((s) => s.field))`.
- Do not add `StateNotifier`, `StateProvider` or `ChangeNotifierProvider` to new code.
- Tests swap in in-memory fakes via `ProviderContainer(overrides: [...])`, and dispose the container with `addTearDown`.

## Speed
- Use `const` constructors and `ListView.builder` with keys.
- Send heavy work to `Isolate.run` or `compute`.
- Wrap animated parts in `RepaintBoundary`. Prefer `FadeTransition` to `Opacity`.
- Set `cacheWidth` and `cacheHeight` on images.
- Check `MediaQuery.disableAnimationsOf(context)` before animating.
- To measure, run `flutter run --profile` with DevTools, add `--trace-startup`, and call `traceAction` from `integration_test`.

## Directional layout
Reach for `EdgeInsetsDirectional`, `AlignmentDirectional` and `PositionedDirectional`. A test may fail any inset whose left and right values differ and which is not directional.

## Architecture test
Write a plain Dart test, `test/architecture/layering_test.dart`. It walks `lib/`, reads each `import` line, and checks it against that folder's allowlist: domain, view model, shared, shell. It also enforces a size limit on files in `presentation/`.

## Analyzer
Enable lints like `avoid_catches_without_on_clauses`, `prefer_final_fields` and `directives_ordering`. The CI gate is a clean `flutter analyze`: it prints `No issues found!` and nothing else.

## Files, media and offline data
- **Where queued files go.** Use `getApplicationSupportDirectory()` from `path_provider`. It is private to the app and hidden from the user.
  - iOS: leave the folder out of iCloud backup with `NSURLIsExcludedFromBackupKey`, and turn on file protection. Pick `NSFileProtectionComplete`, or the `...UntilFirstUserAuthentication` level when a background upload must read the file on a locked phone.
  - Android: set `android:allowBackup` and `dataExtractionRules` yourself, so the exclusion is explicit.
  - Never put data you must keep in `getTemporaryDirectory()`. The OS may wipe it.
- **Encryption at rest.** For sensitive data, use an encrypted database (SQLCipher-backed), or encrypted files whose key lives in `flutter_secure_storage` (keychain or keystore).
- **Database.** Hold one connection per isolate: a background isolate opens its own, or uses `DriftIsolate`.
- **Camera and photos.** Use `image_picker` or `camera`, with `permission_handler`.
  - iOS needs `NSCameraUsageDescription` and `NSPhotoLibraryUsageDescription`. It also needs a plan for limited photo access, where the user shares only some photos. Offer `presentLimitedLibraryPicker`.
  - On Android 13 and later, the system photo picker works without any storage permission.
- **Compression and metadata.** Re-encode to the agreed size with `flutter_image_compress`, or with the `image` package inside an isolate. By default the first drops EXIF. A test with a GPS-tagged photo should prove the tags are gone. Does the product need a field such as capture time? Read it first, then store it as structured data.
- **Big uploads.** Send from the file on disk. A whole video must never go through `readAsBytes()`.
