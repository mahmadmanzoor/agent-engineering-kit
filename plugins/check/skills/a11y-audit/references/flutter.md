# Flutter: accessibility in widget tests

Put the guideline matchers in the widget test of each screen. A cart screen in a shop app is a fine model.

```dart
final semantics = tester.ensureSemantics();
await tester.pumpWidget(const CartScreen());
await expectLater(tester, meetsGuideline(androidTapTargetGuideline)); // 48 dp floor
await expectLater(tester, meetsGuideline(iOSTapTargetGuideline));     // 44 pt floor
await expectLater(tester, meetsGuideline(labeledTapTargetGuideline)); // each tap target is named
await expectLater(tester, meetsGuideline(textContrastGuideline));     // 4.5:1
semantics.dispose();
```

## Scaling test
Wrap the screen in a `MediaQuery` whose `textScaler` is `TextScaler.linear(2.0)`. Pump it, then check that `tester.takeException()` returns null. An overflow shows up there.

## Where each concern lives
| Concern | Use |
|---|---|
| Name for a control | `Semantics(label: ...)` or a `tooltip`. Text comes from `AppLocalizations`. |
| Hide decoration | `ExcludeSemantics` |
| One spoken unit per list row | `MergeSemantics` |
| Reduced motion | Read `MediaQuery.disableAnimationsOf(context)` and stop any `AnimationController` when it is true. |
| Right-to-left | `EdgeInsetsDirectional`, `AlignmentDirectional`, `Directionality` |
| Spoken message after an event | `SemanticsService.announce(message, textDirection)` |
