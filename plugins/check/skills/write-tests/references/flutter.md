# Flutter and Dart testing notes

## Running tests
- One test: `flutter test test/notes/title_limit_test.dart --plain-name "accepts at most 80 characters"`
- One folder: `flutter test test/notes`
- Everything, with analysis first: `flutter analyze && flutter test`

## Tools and techniques
- **Frameworks:** `flutter_test` for unit and widget tests. `integration_test` for flows on a device.
- **Time:** provide the clock through an injectable provider and override it with a fixed one. In widget tests, `tester.pump(duration)` advances time, since the binding fakes it. Use `fake_async` for pure timer logic.
- **Dependency overrides:** with Riverpod, `ProviderScope(overrides: [...])` or a `ProviderContainer`. With other DI, pass dependencies through constructors.
- **Repository fakes:** in-memory classes that implement the repository interface. Keep them in `test/support/`.
- **Network fakes:** a fake HTTP adapter that answers with recorded responses.
- **Local database (Drift):** `NativeDatabase.memory()` per test. It is the real SQL engine with no file. Test migrations with the schema verifier from `drift_dev` against dumped old schemas.
- **Golden images:** `matchesGoldenFile(...)`. Run `--update-goldens` only for a change you meant to make.
- **Accessibility:** `meetsGuideline(androidTapTargetGuideline)`, `labeledTapTargetGuideline`, `textContrastGuideline`.
- **Architecture rules:** a test that reads the import lines under `lib/` and compares them with an allowlist.
- **OS dialogs** (permissions, notifications): `patrol`, or `integration_test` with platform tools, on an emulator or simulator. `flutter_test` cannot tap them.
- **Background work:** test the task body as an ordinary function with fakes. The `workmanager` callback only connects it. Verify scheduling on a device (`/mobile:device-test`).

## Widget test sample
```dart
testWidgets('shows the empty-state text when there are no notes', (tester) async {
  await tester.pumpWidget(ProviderScope(
    overrides: [noteRepositoryProvider.overrideWithValue(InMemoryNotes([]))],
    child: const MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: NoteListScreen(),
    ),
  ));

  final l10n = await AppLocalizations.delegate.load(const Locale('en'));
  expect(find.text(l10n.noNotesYet), findsOneWidget);
});
```

Reading the expected text from the translation files is the default. A hard-coded English literal in the test is fine when the test pins that copy on purpose. A literal inside the widget never is.

## Pitfalls
- `pumpAndSettle` never returns while an endless animation runs. Turn animations off with `MediaQueryData(disableAnimations: true)`, or use `pump(duration)`.
- Wrap each screen in the real localisation delegates, so strings come from the translation files.
