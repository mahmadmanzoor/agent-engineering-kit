# iOS background work

## Pick the mechanism
Examples use a notes app that refreshes and uploads photos.

- **A refresh that can wait.** `BGTaskScheduler`.
  - `BGAppRefreshTaskRequest` is for short jobs. `BGProcessingTaskRequest` is for long ones and can demand power and network.
  - List every identifier under `BGTaskSchedulerPermittedIdentifiers` in `Info.plist`.
  - The system chooses the time.
- **Finishing a task after the user leaves.** `beginBackgroundTask(expirationHandler:)`. You get seconds, not minutes. Always end it.
- **A transfer that must outlive the app.** A background `URLSession` built from `URLSessionConfiguration.background`. The system runs the transfer and relaunches the app when it finishes.
- **Continuous location.** Set `allowsBackgroundLocationUpdates = true`, add the `location` background mode, tune `pausesLocationUpdatesAutomatically` and set `activityType`. Newer iOS also offers `CLLocationUpdate.liveUpdates()` with `CLBackgroundActivitySession`.
- **Waking on movement after termination.** Significant-change location and region monitoring relaunch the app. Restore state at launch.
- **Work triggered by a push.** A silent push (`content-available`). It has a budget and no guarantee.
- **A long task the user started (iOS 26 and later).** `BGContinuedProcessingTask`, with visible progress.

Background modes need a justification for App Review. Never ask for "Always" location before your explanation screen. Expect provisional "Always" too, where the app holds "While Using" until the system asks again.

## Facts to design around
- When the user force-quits from the app switcher, most background work stops until they open the app again. The exception is location relaunch for significant changes and regions.
- Low Power Mode, or Background App Refresh turned off, cuts or stops refresh tasks. Read `ProcessInfo.processInfo.isLowPowerModeEnabled` and `UIApplication.shared.backgroundRefreshStatus`. Surface each as a stop reason.
- With Location Services off for the whole device, the authorisation status reads as denied. Call `CLLocationManager.locationServicesEnabled()` first, so you report the true reason.

## Background uploads
- A background session keeps going while the app is suspended or ended by the system. It relaunches the app to hand over results, through `application(_:handleEventsForBackgroundURLSession:completionHandler:)`.
- Such a session can only upload from a file, using `uploadTask(with:fromFile:)`. Write the multipart body or the raw file to app-private storage first. Uploads from data or a stream fail in the background.
- Tag each task with the record's client id, in `taskDescription` or a header. After a relaunch, that id maps the result to its queue row.
- A force-quit cancels background transfers. The queue must pick them up again on the next launch.
- `BGProcessingTask` fits deferrable work that needs minutes, with `requiresNetworkConnectivity`. It may be delayed for hours.

## Simulator and debugger
- Drive location from the Features menu (City Run, Freeway Drive), or add a GPX file to the scheme.
- Pause in the app and run this in the debugger to fire a scheduled task:
  `e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:@"<id>"]`
- Fire an expiration with `_simulateExpirationForTaskWithIdentifier:`.
- To get a system-style kill, stop the app from Xcode rather than swiping. Then fire the relaunch event.

## Battery
Read the Energy reports in Xcode Organizer. On a real device, in a Release build, record with Instruments (Energy Log or Power Profiler).

## Further reading
- Background URLSession: https://developer.apple.com/documentation/foundation/downloading-files-in-the-background
- BGTaskScheduler: https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler
- Location updates in the background: https://developer.apple.com/documentation/corelocation/handling-location-updates-in-the-background
