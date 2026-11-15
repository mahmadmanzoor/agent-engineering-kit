# Label set (GitHub)

Ask the owner before running this: every label is visible to anyone who can see the repo. `--force` replaces the colour and description of a label that already exists. On another tracker, create the same labels with its own tools.

## The labels

| Group | Name | Colour | Meaning |
|---|---|---|---|
| Kind | `type:feature` | 1D76DB | A capability users can see (one vertical slice) |
| | `type:bug` | D73A4A | Behaviour differs from the spec |
| | `type:chore` | C5DEF5 | Tooling, docs, refactor, spike, upkeep |
| | `type:epic` | 5319E7 | A feature split into several slices (sub-issues) |
| Priority | `P0` | B60205 | Drop everything: safety, data loss or exposure |
| | `P1` | D93F0B | Required for the milestone |
| | `P2` | FBCA04 | Wanted; a workaround exists |
| | `P3` | 0E8A16 | Nice to have; cosmetic |
| Flags | `safety-critical` | B60205 | A silent failure could hurt a person or lose money or data |
| | `privacy` | 5319E7 | Handles personal data, sharing or consent |
| | `needs-device-test` | 006B75 | Check on real devices before release |
| | `spike` | BFDADC | Time-boxed research; it ends in a decision, not merged code |
| | `needs-design` | F9D0C4 | No design yet: agree a state table and a rough flow first |
| State | `in-progress` | 0052CC | Someone is on it |
| | `blocked` | 000000 | Stuck; read the Blocked by comment |
| | `blocked:decision`, `blocked:design`, `blocked:depends-on`, `blocked:account`, `blocked:device` | 444444 | Blocked for that reason |
| Area | `area:server`, `area:client`, `area:web`, `area:mobile`, `area:data`, `area:infra`, `area:ci`, `area:docs` | EDEDED | Touches that module. Edit the list to match the repo. |

## Script

Feed the table to `gh` from a here-document. Each line is `name|colour|description`.

```bash
set -euo pipefail
REPO="${1:?usage: labels.sh owner/repo}"

while IFS='|' read -r name colour desc; do
  gh label create "$name" -R "$REPO" --color "$colour" --description "$desc" --force
done <<'LABELS'
type:feature|1D76DB|A capability users can see (one vertical slice)
type:bug|D73A4A|Behaviour differs from the spec
type:chore|C5DEF5|Tooling, docs, refactor, spike, upkeep
type:epic|5319E7|A feature split into several slices (sub-issues)
P0|B60205|Drop everything: safety, data loss or exposure
P1|D93F0B|Required for the milestone
P2|FBCA04|Wanted; a workaround exists
P3|0E8A16|Nice to have; cosmetic
safety-critical|B60205|A silent failure could hurt a person or lose money or data
privacy|5319E7|Handles personal data, sharing or consent
needs-device-test|006B75|Check on real devices before release
spike|BFDADC|Time-boxed research; it ends in a decision, not merged code
needs-design|F9D0C4|No design yet: agree a state table and a rough flow first
in-progress|0052CC|Someone is on it
blocked|000000|Stuck; read the Blocked by comment
blocked:decision|444444|Blocked by: decision
blocked:design|444444|Blocked by: design
blocked:depends-on|444444|Blocked by: depends-on
blocked:account|444444|Blocked by: account
blocked:device|444444|Blocked by: device
area:server|EDEDED|Touches server
area:client|EDEDED|Touches client
area:web|EDEDED|Touches web
area:mobile|EDEDED|Touches mobile
area:data|EDEDED|Touches data
area:infra|EDEDED|Touches infra
area:ci|EDEDED|Touches ci
area:docs|EDEDED|Touches docs
LABELS
```

## Per-feature labels

`/ship:spec-to-issues` creates one `feature:<slug>` label per feature. It omits `--force`, so a label that exists stays untouched:

`gh label create "feature:<slug>" --repo "$REPO" --description "<Feature>" --color 1D76DB`

## Marking an issue blocked

1. Add `blocked` plus each matching `blocked:<reason>` label.
2. Comment `**Blocked by:** ...` and name what unblocks it. For `depends-on`, write `Blocked by #N`.
3. Once it is unblocked, delete those labels and leave a comment saying so.
