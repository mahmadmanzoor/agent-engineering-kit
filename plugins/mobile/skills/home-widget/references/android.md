# Android widgets and tiles

## Building the widget
- First choice is Jetpack Glance, which gives compose-style widgets through `GlanceAppWidget` and `GlanceAppWidgetReceiver`.
  - Size it with `SizeMode.Responsive`.
  - Wire taps with `actionRunCallback<...>()` (an `ActionCallback`) or with `actionStartActivity`.
- When Glance is not available, write a classic `AppWidgetProvider` that uses `RemoteViews`.
- Preview each state with `previewLayout`, or with a Glance `@Preview`.
- Colours: Material You dynamic colours must map onto your own tokens. Check contrast on light and dark wallpapers.

## Data and refresh
- The app stores the snapshot in `SharedPreferences` or DataStore. Cross-platform bridges such as `home_widget` (Flutter) and `react-native-android-widget` do the same job.
- Refresh through `GlanceAppWidget.update(context, id)` or `updateAll`.
- `updatePeriodMillis` cannot go below 30 minutes. For the live-to-stale flip at `staleAfter`, schedule a WorkManager job or an inexact alarm. Never poll.

## Quick Settings tile
- Subclass `TileService`. Implement `onStartListening` and `onClick`.
- Refresh a tile with `requestListeningState`.
- A toggle must call into the app's own code.

## Ongoing status
Use an ongoing notification. On Android 16 and later, look at progress-centric notifications, also called "live updates".
