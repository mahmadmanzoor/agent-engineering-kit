# Mobile: measuring speed and battery

Rule for all rows: use a release or profile build, on a real device. Include a low-end Android phone with 2 to 3 GB of RAM.

## Android
- **Startup:** Macrobenchmark with `StartupTimingMetric`, or `adb shell am start -W`.
- **Frames and jank:** Macrobenchmark with `FrameTimingMetric`, or a Perfetto trace.
- **Memory:** the Memory Profiler and heap dumps.
- **App size:** APK Analyzer, or `bundletool get-size total`.
- **Battery:** reset with `adb shell dumpsys batterystats --reset`. Run the scenario for an hour. Dump with `adb shell dumpsys batterystats > stats.txt` and keep that file out of git. Open it in Battery Historian. Look at wakelocks and GPS time.
- **Background limits:** force Doze with `adb shell dumpsys deviceidle force-idle`. Also try the App Standby buckets.

## iOS
- **Startup:** Instruments App Launch, or `XCTApplicationLaunchMetric`.
- **Frames and jank:** Instruments Animation Hitches.
- **Memory:** Instruments Allocations and Leaks.
- **App size:** the App Thinning Size Report.
- **Battery:** Energy reports in Xcode Organizer. Instruments Energy Log, on a device.
- **Background limits:** turn Background App Refresh off. Turn Low Power Mode on.

## Cross-platform frameworks
**Flutter**
- Startup: `flutter run --profile --trace-startup` writes `build/start_up_info.json`.
- Build costs: DevTools Performance with "Track widget builds".
- Frame percentiles: an `integration_test` that uses `traceAction`, run with `flutter drive --profile`.
- Size: `flutter build apk --analyze-size --target-platform android-arm64`.

**React Native**
- Hermes profiler and the React DevTools Profiler.
- Flashlight for Android FPS and CPU.
- `react-native-bundle-visualizer` for bundle size.
