---
name: new-repo
description: "Prepare a repository so agents can work in it safely from the first day. Creates the repo and a base commit, protects the default branch, sets up the tracker (milestones, labels, templates) and a bootstrap issue. On the issue branch it records stack decisions, builds a walking skeleton deployed to a test environment, writes AGENTS.md from real commands, adds the placement table with architecture tests, lint and CI, then opens the PR. Use after the idea brief, or when a repo lacks agent rules or CI. Say: 'start a new project', 'make this repo agent-ready', '/ship:new-repo', 'add AGENTS.md', 'set up the repo'."
argument-hint: "[app name, or where the brief lives]"
license: MIT
metadata:
  version: "1.0.0"
  model: opus
  effort: medium
---

# New repo

Prepare the repository for `$ARGUMENTS` (a product name, or its brief) so agents can work in it. With no argument, ask for the brief, or run `/ship:idea-brief` first.

**Run on:** opus at medium. Stack choices and access rules are hard to undo.

## Use it when
- A new product needs a repo, a tracker, a skeleton and CI.
- An existing repo has no `AGENTS.md`, conventions or CI.

**Not for:** adding a feature to a repo that already has its rules (`/ship:feature`).

## Before you start
- Locate the brief and MVP scope. They live in `docs/product/`, or in the chat or scratch folder where `/ship:idea-brief` left them. If they are nowhere, run that skill first.
- Repo already exists: read `README.md`, the manifests, the CI files and `AGENTS.md`. Keep what works. Skip steps already done.
- Let the owner's limits choose the stack (hosting, budget, team skills, platforms), not trends.
- Ask before anything others can see: creating the repo, accounts, labels, protection rules, pushes.

## Steps
1. **Create and protect the repo.** With the owner's OK:
   - Create it. The owner decides public or private: `gh repo create <owner>/<name> --private --clone`.
   - Make a base commit on the default branch (README stub, ignore file, licence) and push it. If the `guard` plugin blocks commits on that branch, prefix this one commit with `GUARD_ALLOW_MAIN=1`.
   - Protect the default branch. Require pull requests and the CI checks (you add those in step 6). Turn on dependency updates and secret scanning if the host has them.
2. **Set up the tracker.**
   - Add milestones taken from the MVP scope.
   - Add labels with the script in [references/labels.md](references/labels.md).
   - Add issue templates (feature, bug) that fit `/ship:file-issue` and `/ship:file-bug`, plus a PR template that fits `/ship:open-pr`.
   - Open a bootstrap issue (`chore: bootstrap the repository`, milestone A). Branch from it as `/ship:start-issue` does: `chore/<n>-bootstrap`. Everything below lands on this branch.
3. **Commit product files and stack decisions.**
   - Put the brief and scope in `docs/product/`.
   - For every choice that is costly to reverse (server, database, client stack, hosting, auth, CI), write a record with `/kit:decision`. Give two real options, the trade-offs, the pick and a revisit date.
   - Favour dull, well-documented tools. Label each item planned or built.
   **Stop if:** the owner has not agreed to every record. Quote that agreement in the PR.
4. **Build the walking skeleton.** The thinnest path that runs end to end, written test-first:
   - One endpoint (a health check and one authenticated read) with its contract and one integration test on a real database.
   - One page or screen that calls the endpoint, plus one UI test.
   - One scheduled job, end to end, if the brief has anything time-based (`/server:add-job`). Schedulers tend to be the riskiest piece.
   - One command starts all local services. Seed data is synthetic.
   - A deploy to a test environment, never production, plus a smoke check. The owner types in any payment details or credentials.
   - Mobile adds: store accounts, app ids, signing keys held as CI secrets, a build flavour per environment, a macOS runner for iOS. Note any store waiting periods. The owner makes the accounts and keeps the keys.
   Lay out folders by `/ship:code-placement` and the stack rules (`/server:server-rules`, `/mobile:app-rules`, `/web:web-rules`). Give each module a short README.
   **Stop if:** a fresh clone cannot reach green tests using the documented commands.
5. **Write AGENTS.md.** Put it at the root. If the team uses Claude Code, add a thin `CLAUDE.md` that points to it. Start from [references/agents-md-template.md](references/agents-md-template.md). Run each command before you list it. Keep the file short.
6. **Add conventions, checks and CI.**
   - Copy the placement table from `/ship:code-placement` into `docs/conventions.md`, using the project's real paths.
   - Write architecture tests for its rows, with allowlists and empty baselines. Break each rule once to see it fail, then revert.
   - Set a strict linter and formatter, with warnings as errors. A single command (say `make check`) runs lint, the format check, architecture tests and every test suite.
   - Set up CI as in `/ship:ci-green`. A public repo gets hosted runners only, never a self-hosted one. Name jobs stably, pin versions, and add a check that the PR links an issue. Register the job names in the protection rule.
   - Optionally turn on the `guard` hooks (secret scan, no commits on the default branch).
   **Stop if:** the single check command is not green both locally and in CI.
7. **Hand off.** Open the PR with `/ship:open-pr` and `Closes #<bootstrap issue>`. Ask `crew:code-reviewer` for the review. Merge through `/ship:merge-gates`. Then begin milestone A with `/ship:feature`.

## Done when
- [ ] The repo, branch protection, labels and milestones exist.
- [ ] Decision records are committed and the owner agreed.
- [ ] A fresh clone passes the check command, and CI is green.
- [ ] `AGENTS.md` lists only commands that were actually run.
- [ ] The bootstrap PR is open and closes its issue.

## Never
- Write feature code before steps 1 to 6 are green. Every later feature copies the first one.
- Commit a secret. Config examples carry placeholders only.
- Create accounts or change protection rules without the owner's OK.
- Attach a self-hosted runner to a public repo. Any pull request could run code on it.

## Next
- **Comes from:** `idea-brief` (ship)
- **Leads to:** `feature` (ship); `decision` (kit) for each stack choice
