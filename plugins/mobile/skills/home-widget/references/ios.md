# iOS widgets and live activities

## Widget extension
- Add a WidgetKit extension target. Write the views in SwiftUI, driven by a `TimelineProvider` or an `AppIntentTimelineProvider`.
- The app and the extension meet in an App Group container: `UserDefaults(suiteName:)` or a plain file.
- Build the timeline with two entries. One is "now". The second sits at `staleAfter` and renders the stale state. Use the `.after(date)` reload policy.
- After the app writes a new snapshot, it calls `WidgetCenter.shared.reloadTimelines(ofKind:)`.
- Preview every state with `#Preview(as: .systemSmall) { ... } timeline: { ... }`.

## Interaction
- From iOS 17, `Button(intent:)` and `Toggle(intent:)` work with App Intents. Each intent calls shared app code.
- From iOS 18, a `ControlWidget` built on App Intents puts a control in Control Center.

## Lock screen and StandBy
- Offer the families `accessoryCircular`, `accessoryRectangular` and `accessoryInline`.
- For the hidden-on-lock-screen state, honour `privacySensitive()` and `@Environment(\.redactionReasons)`.

## Live Activities and Dynamic Island
- Describe the data with `ActivityAttributes` and a `ContentState` (ActivityKit).
- Start the activity from the app. Update it locally or by push: send the ActivityKit push token to your server.
- End it when the task it tracks ends.
- Set the stale time with `staleDate`.

## Cross-platform bridges
Packages such as `home_widget` (Flutter) and `react-native-widget-extension` only carry the snapshot across. You still write the widget UI in SwiftUI.
