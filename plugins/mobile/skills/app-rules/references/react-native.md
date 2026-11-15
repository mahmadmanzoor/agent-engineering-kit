# React Native

Written for TypeScript. Examples use a notes app.

## Where each layer lives
- **View.** Function components in `src/features/notes/presentation/`. Keep them small and fetch nothing inside them.
- **View model.** One hook per screen, such as `useNotesScreenModel()`, or a slice of a store (Zustand or Redux Toolkit). It returns immutable state and action functions. It contains no JSX and never touches the navigation object.
- **Domain.** The `domain/` folder holds plain types, pure functions, repository interfaces, and results as tagged unions, for example `{ kind: 'saved' } | { kind: 'conflict' }`.
- **Repository.** `data/apiNotesRepository.ts` implements the domain interface. Hand it out via a context or a module container. Tests then replace it.
- **Server cache.** TanStack Query can act as the repository's cache. Keep query keys and fetchers in `data/`, and hand out only domain types.
- **Coordinator.** A module that starts once when a session begins. It listens to AppState and NetInfo, and it calls repositories.
- **Service.** The generated OpenAPI client, Turbo or Native Module wrappers, and Expo module wrappers, all in `data/`.
- **Shared module.** `src/shared/`. An eslint rule forbids it from importing anything under `src/features/**`.
- **Feature handle.** `features/<f>/index.ts`, which re-exports the public API and nothing else.
- **Strings.** Message files for i18next or FormatJS, with ICU plurals.
- **Theme.** A single `theme.ts`. An eslint `no-restricted-syntax` rule rejects colour literals in components.
- **Local database.** WatermelonDB, op-sqlite or expo-sqlite, behind a database service, with versioned migrations.

## Enforcement
- Run `eslint-plugin-boundaries` or `dependency-cruiser`. The allowed direction is presentation, view model, data, domain. Features connect only through `index.ts`. Cycles are an error (`no-circular`).
- Switch on `@typescript-eslint/switch-exhaustiveness-check` for result unions.

## Speed
- Render lists with `FlatList` or `FlashList` and a `keyExtractor`.
- Use `React.memo` and narrow selectors such as `useStore(s => s.field)`.
- Use `useMemo` only for derived lists that the view model builds. Never do that work in render.
- Run animations with Reanimated so they stay on the UI thread. Honour `AccessibilityInfo.isReduceMotionEnabled()`.
- Give every image explicit dimensions, through `expo-image` or `FastImage`.
- Take measurements from a release build, using Flipper or the React DevTools profiler, `react-native-performance`, and the Hermes sampling profiler.

## Right-to-left
Lay out with `start` and `end` (`marginStart`, `paddingEnd`) and check `I18nManager.isRTL`. Do not use `left` or `right` for layout.
