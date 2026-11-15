---
name: add-upload
description: "Add or change file uploads, attachments and downloads on the server. Use one upload reader and one storage port, pick a transfer method on purpose, detect type from bytes, fail visibly on size caps, re-encode images and strip metadata, check membership on reads, finish parent records only when every attachment is confirmed, clean up orphans, and test it all. Use for uploads, attachments, avatars and downloads. Say: '/server:add-upload', 'presigned URL', 'multipart upload', 'image upload', 'attach photos', 'store files', 'avatar upload', 'upload a file'."
argument-hint: "[what gets uploaded, who uploads it, what it hangs off]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: high
---

# Add an upload

Build or change the upload described by `$ARGUMENTS`. No argument? Ask about: the file kind and its usual and largest size, the uploader, the readers, offline creation, and retention time.

**Run on:** opus at high. Uploads can leak personal data, since photo metadata holds a location, and can lose data without a sound, such as a record saved minus its files.

## Use it when
- You add or change an upload, an attachment or a file download.

**Not for:** the endpoint contract on its own (`server:add-endpoint`). Use that skill next to this one.

## Before you start
Read `AGENTS.md` and the placement table. Check whether an upload reader and a storage port with adapters exist already. If so, reuse them. A feature with its own storage class is a design flaw to fix. Do not copy it. Find the storage for each environment: local disk or a container in development, an object store in production. Find the client: web, or mobile with offline or background upload (`mobile:offline-queue`, `mobile:background-work`).

**Stop if:** any of these is unknown: the upload reader, the port and its adapters, or the access unit that rules on who reads a file.

## Steps
1. **Pick the transfer method.**
   - **Multipart through the API.** For small files (a few MB) and simple clients. The reader streams to the storage port. It never holds a whole file in memory.
   - **Presigned direct upload.** For larger files, many uploads, or mobile. The API hands out a short-lived URL that allows one object, one size limit and one type. The client uploads and then confirms. The server checks the stored object.
   - **Resumable or chunked.** For very large files or poor networks. Chunks share an upload id. Abandoned uploads expire.

   Write the choice and the limits in the spec. Switching methods later needs a decision record (`kit:decision`).
2. **Design the parts.**
   - **Reader:** one reader, at the edge. It detects the type from the bytes, not from the name or the declared type. It enforces the size cap whether or not a length was declared, and allows only listed types. Handlers never read a raw body.
   - **Storage:** one port with `put`, `get`, `delete` and `presign`. Each provider gets one adapter, picked by config, and all adapters pass the same contract tests. The use case chooses the key layout. No feature owns a storage class.
   - **Names:** object keys are random and sit outside the web root. The user's filename is metadata and nothing more.
   - **Processing:** re-encode images on the server. That also removes embedded scripts and malformed data. Strip metadata such as location and device ids. When the product needs a value (capture time, a place kept as evidence), store it as explicit, consented, structured data on the record. Do not leave it inside the file. Mobile clients also strip on the device before they upload.
   - **Reads:** pass through an endpoint that checks membership, or use a short-lived signed URL handed out once access is confirmed. Personal files never live in a public bucket.
   - **Parent records:** a record with attachments is complete only when every attachment is confirmed. Until then it stays a draft. Each attachment's client id is its permanent idempotency key (`server:add-endpoint`).
   - **Failures:** a file that is too large, the wrong type or fails a scan produces a visible problem with a stable code. It is never dropped silently. A client queue must not discard a bad file without telling the user.
   - **Cleanup:** a scheduled job (`server:add-job`) removes orphans after a stated delay. Deleting an account deletes its files.
   - **Scanning:** for files that other people download, scan before the file becomes readable. "Pending scan" is a state.
   - **Limits:** use the project's limiter for per-user rate and quota caps.

   **Stop if:** the design lacks the reader, port, transfer method, metadata rule, completion rule or cleanup. Send it to `ship:plan-review`. Personal files also need `check:security-review`.
3. **Write the tests first.** Drive the real entry point against real storage, or a containerised engine (an S3-compatible container is fine) (`check:test-rules`). Cover:
   - upload then confirm: the record completes and an allowed caller can read the file;
   - forbidden callers: a non-member sees not found on upload, confirm and read. A member who was removed can no longer read. Signed URLs already issued run out fast;
   - bytes that do not match an allowed type are rejected with the code, even when the extension looks right;
   - an oversize file gets a visible problem with the code, and nothing is stored;
   - a test image that carries GPS data is stored without it;
   - one attachment sent twice with the same client id leaves one object and one row, and gets the original answer;
   - a parent missing an attachment stays pending, then completes when the last one arrives;
   - orphan cleanup deletes unconfirmed objects past the delay and leaves everything else.
4. **Build and verify.** Follow `server:server-rules`. Reader and adapters sit in their layers, and the use case owns the keys and the completion rule. Run the adapter contract tests for each storage adapter. In the PR, spell out the size limits, how metadata is handled, who may read, and the cleanup delay.

## Done when
- [ ] Every step 3 test passes, with command and output shown.
- [ ] The contract tests pass for every storage adapter.
- [ ] A stored test image has no location or device metadata.
- [ ] Limits, access rule and cleanup delay are written in the PR.

## Never
- Never give a feature its own storage class, and never add a second upload reader.
- Never believe a filename or a declared content type.
- Never serve uploaded files from the web root.
- Never let stored files keep GPS, device or other location metadata.
- Never discard a file without showing an error.

## Next
- **Comes from:** `build`, `write-spec`, `plan-review` (ship); `add-endpoint` (server)
- **Leads to:** `add-migration`, `add-job` (server); `check:security-review`; `mobile:offline-queue`
