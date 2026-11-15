# Mobile accessibility: Android, iOS, React Native

## Side by side
**Screen readers.** TalkBack on Android, VoiceOver on iOS.

**Naming a control**
- Android: `contentDescription`. In Compose, `Modifier.semantics { contentDescription = ... }`.
- iOS: `accessibilityLabel`, plus `accessibilityValue` and `accessibilityHint` when needed.

**Grouping several views into one spoken item**
- Android: `mergeDescendants`, or tune with `importantForAccessibility`.
- iOS: `accessibilityElements`, or `.accessibilityElement(children: .combine)` in SwiftUI.

**Hiding decoration**
- Android: `importantForAccessibility="no"` or `invisibleToUser()`.
- iOS: `isAccessibilityElement = false`, or `.accessibilityHidden(true)`.

**Speaking a change out loud**
- Android: `announceForAccessibility`, or a live region.
- iOS: `UIAccessibility.post(notification: .announcement, ...)`.

**Text size**
- Android: size text in `sp`. Test with font scale 2.0.
- iOS: support Dynamic Type. Test at the largest accessibility size.

**Reduced motion**
- Android: the "Remove animations" setting, which zeroes the animator duration scale.
- iOS: check `UIAccessibility.isReduceMotionEnabled`.

**Minimum target:** 48x48 dp on Android, 44x44 pt on iOS.

**Automated audits**
- Android: Accessibility Scanner by hand, and `AccessibilityChecks.enable()` inside Espresso tests.
- iOS: the Accessibility Inspector audit by hand, and `XCUIApplication().performAccessibilityAudit()` in UI tests.

## React Native
Props: `accessibilityLabel`, `accessibilityRole`, `accessibilityState`. Calls: `AccessibilityInfo.announceForAccessibility` and `AccessibilityInfo.isReduceMotionEnabled()`. In tests, query with Testing Library's `getByRole` and `getByLabelText`, so a missing label fails the test.
