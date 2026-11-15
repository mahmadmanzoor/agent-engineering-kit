---
name: app-rules
description: "Rules for how a mobile app is laid out and written on any stack: view, view model, repository and service layers with may and must-not rules, coordinators for long loops, feature folders and a shared module, immutable state, closed result types, visible errors, permission flow, offline storage, low-end performance, strings, RTL and the architecture test that enforces them. Use when you are deciding where app code goes, starting a screen, or reviewing a mobile diff. Say: '/mobile:app-rules', 'which layer is this', 'view model', 'new screen structure', 'permission flow', 'app architecture', 'is this widget too big'."
argument-hint: "[change, file needing a home, or diff]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# App rules

Use these layer rules on `$ARGUMENTS`: a change, a file that needs a home, or a diff. With no argument, use them on the change you are making.

**Run on:** opus at medium. A wrong layer or a hidden error is expensive to undo later.

## Use it when
- You add code to a mobile app or start a new screen or feature.
- You review a mobile diff for layering, state, errors, permissions or speed.

**Not for:** background jobs (`background-work`), a core shared by both platforms (`shared-core`), a screen built from a design (`design-to-screen`), general placement rules (`code-placement` in `ship`).

## Before you start
Read `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, the app README and any decision records. Read the manifest to learn the stack, then open one reference:
[references/flutter.md](references/flutter.md), [references/react-native.md](references/react-native.md), [references/android-native.md](references/android-native.md), [references/ios-native.md](references/ios-native.md).

Collect the project's own names for layers and folders, its state tool, theme file, string files and architecture test. Where the project and this skill disagree on a fact, the project wins. No layer rules or no architecture test? Say so, and offer to add them (`new-repo` in `ship`).

## Steps
1. **Give every file a layer.** Each layer has one job, a short list of things it may call, and a list of things it must not do. A notes app serves as the example.
   - **View.** Draws the screen: layout, theme, strings, animation, navigation. Passes user events to its view model. May call: its view model only. Must not: call a repository or service, hold business rules, or catch business errors.
   - **View model.** Holds one immutable screen state and exposes each action as a method. Joins data from several repositories. May call: repositories and domain functions. Must not: import UI types or a UI context, call a service, or navigate on its own.
   - **Domain.** Immutable models, repository interfaces, pure rules and validators. May use: core language code and other domain code. Must not: do I/O, or import UI, state-library or generated types.
   - **Repository.** The single source of truth for one kind of data, such as notes. Fetches, caches and exposes streams. Turns service models into domain models and transport errors into domain errors. May call: services. Must not: know another repository or a coordinator, or return generated types or transport errors.
   - **Coordinator.** A loop that runs over time: reconnect, reconcile, retry until the server confirms. May call: repositories, services, domain rules. Must not: be imported by a repository, or contain rules. The rule is a domain function and the loop applies it.
   - **Service.** A stateless wrapper over one outside source. It keeps no state and holds no rules.

   Consequences:
   - Every user action reaches data through a view-model method. A read-only list may watch a repository stream.
   - Two repositories never talk. A view model or a domain function joins their data.
   - A screen and its view model pair one to one. A dialog that only collects input needs no view model. State two screens share belongs in a repository.
   - Name each repository method for the user action it serves, for example `renameNote(id, title)`. Do not write one `update(...)` with optional fields.
   - After a write, the screen reloads from the single source of truth.
   - Generated and bridge types stay in the data layer. The repository maps them to domain models, and a test covers the mapping.
   - Add a use-case class only when two view models need the same logic across several repositories.

   **Stop if:** a new file fits no layer. That is a design question for `plan-review` (`ship`).

2. **Keep features apart.**
   - Lay out `features/<feature>/{data,domain,presentation}`, or the project's own names.
   - One feature may use another only through its domain or through one public handle. A handle is a file that re-exports and holds no code.
   - Features never form a cycle. A type that two features need moves down into the lower feature or into the shared module.
   - When feature A's screen appears inside feature B's flow, the app shell wires them together. B does not import A.
   - The shared module states its purpose and keeps an allowlist: session, clock, failures, backoff, value types. A test proves it imports no feature. Anything with screens of its own is a feature.
   - The app shell also keeps an allowlist: app root, router, theme, config, crash reporting, shared design-system parts.

3. **Make state, models and errors safe.**
   - Models and state never change in place. A screen has one state value, or a loading, data, error wrapper.
   - Model expected outcomes as closed result types. The compiler then lists every unhandled case.
   - Each catch names its error type and either shows the failure or rethrows. An empty catch is a defect.
   - Safety-critical actions show what really happened. Never show success early.
   - Take enum labels from string resources, not from the enum's name.
   - Inject the clock. Views and view models never read system time.

4. **Treat permissions openly.**
   - Put an in-app screen before every system prompt. It tells the user why you ask and what breaks if they refuse. Never fire a prompt cold at first launch.
   - Cover every answer: granted, denied, limited or approximate, revoked later in settings. Say what no longer works and link to settings.
   - Ask for always-on background access only after foreground access, and explain it separately.
   - Check again each time the app returns to the foreground.
   - Ship a new permission together with a store release, reviewer notes and a revised privacy declaration (`deploy-check` in `ship`).

   **Stop if:** a denied or revoked permission leaves the feature quietly doing nothing.

5. **Hide offline storage behind the repository.**
   - Treat the local database as a service: tables, access objects, migrations, no rules.
   - The repository serves local data first, then refreshes over the network. Its writes follow `offline-queue`. If the action must reach the server right now, it writes online only.
   - A safety-critical action never sits silently in a queue. Show a "not sent yet" state, keep retrying, and give the user a fallback path.
   - Change the schema only through versioned migrations. Test that data from the previous build still reads.

6. **Hold to the speed rules.** The project owns the budgets. Measure with `perf-check` (`check`), in a release or profile build, on a low-end device.
   - Watch the smallest slice of state from the smallest widget. Give a ticking clock its own widget.
   - Keep sorting, filtering, formatting and parsing out of the render path. Do them once per state change in the view model.
   - Use lazy lists with stable keys wherever the list can grow.
   - Run heavy work (large parses, images, sorts) off the main thread.
   - Animate opacity and transform. Skip blur and shadow in parts that scroll or animate.
   - Decode each image at the size it is shown.
   - Dispose every controller, subscription, timer and animation. Stop animations when off screen or when the user prefers reduced motion.
   - Do nothing heavy before the first frame. Start plugins lazily.

7. **Strings, direction, theme, access.**
   - Each user-facing string is a keyed resource with a description. Plurals and placeholders use the message format.
   - Use start and end, never left and right, so right-to-left locales mirror.
   - Take colours, radii, spacing and type from a single theme source. When a token is missing, add it there. A literal in a view fails a test. The contrast rule lives in `design-to-screen`.
   - Every interactive element has a label and a target of at least 48 dp or 44 pt (`a11y-audit` in `check`).

8. **Enforce it with an architecture test.** Start from an empty baseline. The test fails when:
   - generated or bridge code leaks out of the data layer;
   - a feature imports another except through domain or a handle, a handle contains code, or features form a cycle;
   - a domain file imports outside its allowlist, or the shared module imports a feature;
   - the app shell contains a file its allowlist does not name;
   - a raw colour value sits anywhere but the theme;
   - a view model imports UI types, a view uses a repository, or a repository imports a coordinator;
   - a test fake declares app-level bindings;
   - a presentation file grows past the size limit (say 320 lines).

   CI also runs lint and the formatter.

## Done when
- [ ] Every new file sits in a named layer and folder, and nobody edited generated code.
- [ ] No view touches a repository or service. No view model imports UI types.
- [ ] Repositories return domain models or closed results, never generated types or transport errors.
- [ ] Features connect only via domain or a handle. No cycles.
- [ ] Each permission is explained before its prompt, and each denial is visible to the user.
- [ ] Strings, theme tokens and directional layout replace every literal.
- [ ] Every catch is typed and visible. The architecture test and lint pass (paste the output).

## Never
- Copy code that breaks a rule just because it is already in the repo. Fix it or file an issue.
- Let a stack reference override the layer rules.
- Write personal data to logs or crash reports.

## Next
- **Comes from:** `build` (`ship`), `plan-review` (`ship`), `design-to-screen` (`mobile`), `review-code` (`check`)
- **Leads to:** `background-work`, `offline-queue`, `shared-core` (`mobile`); `perf-check` (`check`)
