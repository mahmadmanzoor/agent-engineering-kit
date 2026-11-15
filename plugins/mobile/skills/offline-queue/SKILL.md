---
name: offline-queue
description: "Design or change the on-device outbox that holds data created offline and never loses it silently. Records land in a durable local queue before anything else, carry a permanent client-made id the server dedupes on, upload through one uploader at a time in batches with capped backoff, and send attachments one by one with the parent completed last. Losses are planned and listed in the spec. Unreadable queues, full storage and poison records all end visibly. Use when an app sends data that may be created offline. Say: '/mobile:offline-queue', 'offline first', 'sync queue', 'upload when back online', 'lost data offline', 'duplicates after retry'."
argument-hint: "[queued record type, or the change to the queue]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# Offline queue

Design or change the on-device queue in `$ARGUMENTS`: the kind of record that is queued, or the change itself. With no argument, ask two questions: what must the app send, and what is the cost of losing one record?

**Run on:** opus at medium. A bad queue loses user data without a trace, or it creates duplicates.

Phones stay offline for days, die mid-upload and run out of space. The promise: every record arrives exactly once. A loss can happen only when someone planned it, the spec accepts it, and a test covers it. Every other failure retries until the record arrives.

## Use it when
- Your app sends data that users may create while offline.
- Records go missing, appear twice, or stick after a retry.

**Not for:** the background job itself (`background-work`), or the server endpoint (`add-endpoint` in `server`).

## Before you start
Read `AGENTS.md`, `CLAUDE.md`, the decision records and any queue code that exists (database service, uploader, retry timer). Locate:
- the server endpoint that accepts batches, and its dedupe rule (`add-endpoint`, `server`);
- the shared core (`shared-core`) and the background mechanism behind uploads (`background-work`);
- the local database and its migration tests (see the stack notes in `app-rules`).

**Stop if:** any of these is unknown: where records are written, which component uploads them, how the server spots a repeat.

## Steps
1. **Design the queue.** Settle every topic below. Write the design down, above all the list of losses, in the spec or a decision record. The examples assume a shop app that queues orders and receipt photos.

   *Writing and identity*
   - **Write path.** The local store gets the record before anything else happens. The write runs on the queue's own thread and never on the main thread.
   - **Identity.** The client makes a random id when it creates the record, and that id stays for good. The server keeps that id as a unique key on the stored record. A store with an expiry will not do. Then a phone that was offline for a week cannot make a duplicate. When the server sees the id again, it returns the original resource with a success status. It never returns an error or a second row.
   - **Single flight.** Only one uploader runs per queue. The foreground trigger, the background worker and the retry timer all take one lease: a database row with an expiry, or the OS unique-work feature.
   - **Schema.** Version the stored format, so a new build can read rows an older build wrote.
   - **Time.** Each record holds the device time and a monotonic or server-corrected time. The server tolerates clock skew and flags it. It does not reject the record.

   *Sending*
   - **Batching.** Group small records into one request, capped at N records or K kB. A row is deleted only once the server confirms it, and each confirmation is matched by client id.
   - **Retry.** Back off with jitter and a ceiling, for example 30 s doubling up to 5 min. One rule in the core sets the delay. The OS scheduler's own backoff can grow to hours, so do not rely on it.
   - **Server answers.** Keep a table in the core.
     - Success, including "already have it": delete the row.
     - Retryable (timeout, 5xx, 429 with its delay): keep the row and retry.
     - Auth expired: refresh, then retry.
     - "This device may no longer send": take the planned-loss path if the spec accepts it. Otherwise show a visible blocked state.
     - A whole batch refused as invalid (400, 413): split it to find the poison record.
     - A single record or file refused alone (invalid, too large): never drop it silently. Move it to a visible "needs attention" state where the user can see, fix or discard it. Count it and report it.

   *Attachments*
   - Keep files out of the row. Store each in app-private storage that cloud backup skips, encrypted when sensitive. A child row refers to it by path, hash and size.
   - Before queueing, compress the file and strip metadata: EXIF, location, device serials. If a field such as capture time is needed, keep it as structured data (`security-review` in `check`).
   - Upload each file by itself, resumable or chunked when large (`add-upload` in `server`).
   - The parent completes only when every child is confirmed. Delete a file only after its parent is confirmed.
   - Before accepting a new attachment, check free space. Tell the user when it is low.

   *Losses and failures*
   - **Planned losses.** Allow only the losses the spec lists, with numbers. Typical entries: sign-out, another account signing in, the server telling this device to stop sending, and a retention limit that removes the oldest records once they pass N days or M records. Count and report each one. No other path may drop a record.
   - **Data that must never be lost** (submissions, payments, evidence) has no default losses. Block sign-out and account switch while records are unsent, and show how many there are so the user can wait or export. A retention limit turns into a visible warning. The owner decides any exception.
   - **Unreadable queue.** A read error, a damaged row, or a confirmed row that cannot be deleted ends the run with a retry. It is never "nothing to send" and never "done".
   - **Storage failure.** After N failed writes in a row (say 3), stop with a visible `storage unavailable` problem. Tell the user. If other people depend on the data, tell the server too.
   - **Privacy.** Personal data stays in app-private storage, out of backup, encrypted when sensitive. Clear it on sign-out only when nothing unsent remains, or when the spec accepts the loss. Keep record content out of logs.

   **Stop if:** the loss list is not accepted in the spec (and is not empty), some other path fails to retry, or the dedupe key is not the permanent client id.

2. **Write the tests first**, in the tests of the core or the queue module (`test-first` in `check`). Start with failure paths.

   *Connectivity and crashes*
   - Offline for an hour: records stay, then all upload on reconnect, in order, with no gap.
   - Killed after the write and before the upload: the record uploads after restart.
   - Killed after the server confirmed and before the delete: the server dedupes the repeat. One row, original returned, success answer.
   - Killed in the middle of an upload (mid-batch or mid-file): it resumes, with one row and one file.
   - Two uploaders start at once: one runs, and the server sees each record once.
   - A repeat after a long offline stretch, beyond any idempotency window (say 8 days): still one row.

   *Attachments and space*
   - A parent has three attachments and the second upload fails: the parent stays pending, only the missing part retries, and the parent completes after all three are confirmed.
   - The server refuses one file as too large: it moves to "needs attention", stays visible, and blocks and drops nothing else.
   - Disk space is low: a new attachment is refused with a message, and queued data is untouched.

   *Errors*
   - Server 5xx or timeout: retries follow the exact backoff sequence, capped.
   - A batch refused as invalid: it is split, the poison record is isolated and counted, and the rest are sent.
   - An unreadable queue or damaged row: the run ends with a retry, not "done".
   - Three failed writes: blocked with the storage problem, and reported.

   *Losses and data*
   - Each planned loss removes exactly the listed records, counts them and reports them. No other path removes any. With a no-loss spec, sign-out is blocked while records are unsent.
   - A retention limit drops the oldest first, at exactly the stated numbers.
   - Rows written by the previous build still read. Use real bytes from that build, not fixtures typed by hand.
   - Clock skew of one day in either direction.

   Add server tests as well: one client id sent twice gives one row and returns the original both times, including after any idempotency window.

3. **Build it.** If the queue lives in the shared core, follow `shared-core`: rules in the core, database and HTTP as adapters that return failure values. If it lives in app code, follow `app-rules`: a repository plus a database service. Uploads run through the mechanism in `background-work`.

4. **Verify.** Run the tests on every target. Do an emulator pass with airplane mode and process death. Then run the offline and reboot rows of `device-test`.

   **Stop if:** a test from step 2 is missing, or a device row is neither done nor listed as open.

## Done when
- [ ] Every test from step 2 exists and passes (paste the output).
- [ ] The loss list is accepted in the spec, or empty.
- [ ] Sending a client id twice makes the server return the original, and a server test shows it.
- [ ] Device rows are done, or listed as open in the PR.

## Never
- Drop a record silently. A new loss path needs a spec update, a counter and a test.
- Report "done" or "empty" when something failed.
- Add a second retry layer, for example in the HTTP client. The queue's own rule owns retry.
- Let a safety-critical action sit unseen in the queue. Show "not sent yet" in the UI and offer a fallback.
- Run two uploaders together. A second trigger joins the first or waits.
- Store files inside rows, or delete a file before its parent is confirmed.

## Next
- **Comes from:** `write-spec`, `build` (`ship`); `background-work` (`mobile`)
- **Leads to:** `add-endpoint` (`server`) for the dedupe endpoint; `shared-core`, `device-test` (`mobile`)
