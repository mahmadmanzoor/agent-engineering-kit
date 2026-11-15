# Astro

By default Astro ships no client script, which matches the content-site rules.

## Folder map
- `src/pages/` holds routes only. Each is a three-line wrapper such as `<Landing locale="en" />`, one per locale.
- `src/layouts/` holds `Base.astro` (head, CSP meta, fonts, header, footer) and `Prose.astro`.
- `src/components/`:
  - `Landing.astro` is the composition. It sets the Base layout, the section order, the JSON-LD and the single `<script>` import.
  - `sections/` has one section per file.
  - Shared parts such as `<Shared>.astro` sit beside them.
- `src/i18n/` has `en.ts` as the source, other locales typed against it, and `index.ts` with `t()` and the locale list.
- `src/scripts/` has the `site.ts` entry that calls `init*()`. A large behaviour gets its own file.
- `src/styles/global.css` holds `@font-face`, the tokens (custom properties on `:root`) and base styles.
- `public/` holds `fonts/`, `media/`, the favicon and `robots.txt`.
- `scripts/` at the repo root holds build guards and their tests. Node runs them. They are never shipped.

## Working rules
- Declare `interface Props` in each component's frontmatter and read `Astro.props`.
- The composition component carries the one processed `<script>`. It imports `site.ts`, so Astro bundles a single module.
- Do not use `is:inline`, except for JSON-LD: `<script type="application/ld+json" set:html={...} />`.
- In `astro.config.mjs`, set `output: 'static'` and choose `build.inlineStylesheets` as the project decided. Scripts are never inlined, because the CSP says `script-src 'self'`.
- Use `<Image>` or `<Picture>` from `astro:assets` for images under `src/`. Pre-rendered media in `public/` needs `width` and `height`.
- Set SVG colours through `style`, for example `style="fill: var(--brand)"`, and avoid presentation attributes.
- Skip UI framework islands (`client:*`), unless a decision record approves one.

## Checks
- `astro check` covers types, locale dictionaries included. Run eslint too.
- Node unit tests, run as `node --test scripts/*.test.mjs`, read `dist/` and assert five things: no third-party URLs, no inline scripts, a headers file is present, no hex colours in components, and tokens that match the source.
- Playwright runs on the built `dist/`, served statically, with axe.
- Full run: `npm run lint && npm run build && npm test && npm run e2e`.

## Self-check greps
Each should return nothing for new code.

```bash
# inline scripts other than JSON-LD
grep -rn 'is:inline' src/ | grep -v 'ld+json'
# framework islands
grep -rn 'client:' src
# hex colours in components, layouts and pages
grep -rnE '#[0-9a-fA-F]{3,6}\b' src/components src/layouts src/pages
```
