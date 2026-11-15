# Android background work

## Pick the mechanism
Start from what the job needs. Examples use a notes app that syncs and uploads attachments.

- **A session the user started and watches** (say, a long export). Run a foreground service.
  - Declare the right `foregroundServiceType`: `location`, `dataSync`, `mediaPlayback`, `connectedDevice` and so on.
  - Declare the permission that pairs with it, `FOREGROUND_SERVICE_*`, and show an ongoing notification that carries actions.
  - Android 14 and later demand the type. Android 12 and later limit starting one from the background.
- **Work that can wait, with conditions.** Use WorkManager: `OneTimeWorkRequest` or `PeriodicWorkRequest`, plus `Constraints(requiredNetworkType = CONNECTED)`. A periodic job cannot repeat faster than every 15 minutes.
- **A retry delay you choose.** Let the worker schedule its own next run, for example 30 s doubling up to 5 min. WorkManager's built-in backoff can stretch to hours.
- **A moment on the clock.** `AlarmManager.setExactAndAllowWhileIdle` needs `SCHEDULE_EXACT_ALARM` or `USE_EXACT_ALARM`. Skip it unless the user set the alarm.
- **Coming back after reboot or update.** Register a `BroadcastReceiver` for `BOOT_COMPLETED`, `LOCKED_BOOT_COMPLETED` (direct boot) and `MY_PACKAGE_REPLACED`. Restart only when the user had the feature switched on.
- **Location while closed.** Use the Fused Location Provider with adaptive priority and interval. On Android 11 and later, request `ACCESS_BACKGROUND_LOCATION` on its own, after foreground access, through settings.
- **Notifications.** Android 13 and later need the `POST_NOTIFICATIONS` runtime permission.

## Doze, App Standby and vendor killers
- Doze holds back jobs, alarms and network on an idle phone. App Standby buckets cap how often work may run.
- `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` needs an explanation to the user and a use case that store policy accepts. Otherwise do not ask.
- Many makers add their own killers, named "auto-start" or "battery saver". https://dontkillmyapp.com lists the settings by vendor. From the reliability check, send users straight to those screens. A heartbeat reveals when a kill happened.

## Long transfers on current versions
- **User-initiated data transfer jobs** are the intended route for an upload or download the user began. They need Android 14+, `JobInfo.Builder.setUserInitiated(true)`, the `RUN_USER_INITIATED_JOBS` permission, and a start while the app is visible. They can run long, show a notification and outlive backgrounding. WorkManager does not offer them, so call `JobScheduler`. On older versions, fall back to a `dataSync` foreground service.
- **`dataSync` foreground services have a time cap** from Android 15 (roughly 6 hours per 24). The system calls `onTimeout()` and the service must stop. Save progress, let the queue resume later, and report the reason.
- Expedited WorkManager work (`setExpedited`) fits short, important uploads. It has a quota. When the quota runs out, it may run as an ordinary job.
- Send big files from disk over a resumable protocol. Never hold a whole file in memory.
- Call `enqueueUniqueWork(name, ExistingWorkPolicy.KEEP, ...)` so a second trigger cannot start a parallel upload.

## Emulator commands
Swap in your emulator id for `<serial>`, and always pass `-s <serial>`. A real phone then stays safe from a stray command.

- Fake unplugging: `adb -s <serial> shell dumpsys battery unplug`. Undo with `dumpsys battery reset`.
- Enter Doze: `adb -s <serial> shell dumpsys deviceidle force-idle`. Leave it with `deviceidle unforce`.
- Push the app into a low standby bucket: `adb -s <serial> shell am set-standby-bucket <package> rare`.
- Kill the process politely: `adb -s <serial> shell am force-stop <package>`. The app will not restart itself until someone opens it.
- Kill it the way the OS does, on a userdebug image: run `adb -s <serial> root`, then `adb -s <serial> shell kill -9 $(adb -s <serial> shell pidof <package>)`.
- Move the device: `adb -s <serial> emu geo fix <lng> <lat>`. Longitude goes first.
- Run a scheduled job right now: `adb -s <serial> shell cmd jobscheduler run -f <package> <job-id>`.

Note that `adb shell am kill` leaves a foreground service running.

## Measuring battery
1. Reset the counters with `adb shell dumpsys batterystats --reset`.
2. Play the scenario for an hour on a real device that is unplugged.
3. Save the numbers with `adb shell dumpsys batterystats > stats.txt`. Keep that file out of git. Look at wakelocks, GPS time and jobs.

Battery Historian draws the same data as a timeline.

## Further reading
- Doze and App Standby: https://developer.android.com/training/monitoring-device-state/doze-standby
- Foreground services: https://developer.android.com/develop/background-work/services/fgs
- Persistent work with WorkManager: https://developer.android.com/develop/background-work/background-tasks/persistent
- Location in the background: https://developer.android.com/develop/sensors-and-location/location/background
