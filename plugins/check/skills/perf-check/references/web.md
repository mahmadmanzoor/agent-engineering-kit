# Web: measuring speed

## Budgets
Core Web Vitals, at the 75th percentile on throttled mobile:

| Metric | Limit |
|---|---|
| LCP | 2.5 s or less |
| INP | 200 ms or less |
| CLS | 0.1 or less |

## Tools
- **Lighthouse CI** (`@lhci/cli`). Run `lhci autorun` on the built site with assertions such as `categories:performance >= 0.9` and `largest-contentful-paint <= 2500`. Set `numberOfRuns: 3` and read the median.
- **Bundle size.** Use `size-limit` or the bundler's analyzer (`vite-bundle-visualizer`, `webpack-bundle-analyzer`, the `next build` report). Set a CI limit for each entry point. A PR that adds JS or blocking CSS must state the size change.
- **Profiling.** Chrome DevTools Performance panel at 4x CPU slowdown. The Coverage tab shows unused JS and CSS.
- **Real-user data.** The `web-vitals` library, sending to your own analytics with no personal data.

## Fixes that usually pay off
- Give images `width` and `height`, and lazy-load them.
- Host fonts yourself, set `font-display: swap`, and preload them.
- Keep third-party scripts out of the render path.
- Send less JavaScript: render on the server, use islands, use `<details>` where a JS toggle would go.
