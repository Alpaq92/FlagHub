# Repository automation

This directory configures the GitHub-side workflow for FlagHub: PR reviews, security scanning, conditional auto-merge, rebuild + release on every merge, and a daily sync from upstream `madebybowtie/FlagKit`.

## Overview

```mermaid
flowchart TD
    UP([Daily cron 02:17 UTC]):::cron
    UP --> SYNC[sync-upstream.yml<br/>fetch madebybowtie/FlagKit master]:::sync
    SYNC --> SYNC_PR([Sync PR<br/>chore sync ...])
    SYNC_PR --> PR

    PR([PR opened]):::start

    PR --> CR[CodeRabbit auto-review<br/><code>.coderabbit.yaml</code>]:::review
    PR --> CI[CI<br/><code>swift build · test · podspec lint</code>]:::check
    PR --> CQ[CodeQL<br/><code>Swift security-and-quality</code>]:::check
    PR --> SEC[Security<br/><code>gitleaks · deps · Trivy</code>]:::check

    CR --> GATE
    CI --> GATE
    CQ --> GATE
    SEC --> GATE

    GATE{Approved by CODEOWNER /<br/>collaborator / coderabbitai?<br/>All checks green?<br/>7 days elapsed?}:::gate

    GATE -->|yes| MERGE[auto-merge.yml<br/>squash → main]:::merge
    GATE -.bypass.-> MANUAL[Manual merge via PR UI]:::bypass
    MANUAL --> MERGE

    MERGE --> CL[changelog.yml<br/>prepend <code>[Unreleased]</code> entry]:::post
    MERGE --> RL[release.yml<br/>swift build · xcframework · artefact]:::post

    RL --> TAG{<code>v*.*.*</code> tag?}:::gate
    TAG -->|yes| GHR([Publish GitHub Release]):::release

    classDef start   fill:#0969da,stroke:#0969da,color:#fff
    classDef review  fill:#a371f7,stroke:#a371f7,color:#fff
    classDef check   fill:#1f883d,stroke:#1f883d,color:#fff
    classDef gate    fill:#bf8700,stroke:#bf8700,color:#fff
    classDef merge   fill:#1f883d,stroke:#1f883d,color:#fff
    classDef bypass  fill:#6e7681,stroke:#6e7681,color:#fff
    classDef post    fill:#0969da,stroke:#0969da,color:#fff
    classDef release fill:#cf222e,stroke:#cf222e,color:#fff
    classDef cron    fill:#1f883d,stroke:#1f883d,color:#fff
    classDef sync    fill:#a371f7,stroke:#a371f7,color:#fff
```

## Files

| Path | Purpose |
|---|---|
| `.coderabbit.yaml` | CodeRabbit profile. Auto-reviews every PR, skips image assets, runs LanguageTool + markdownlint + shellcheck |
| `.github/CODEOWNERS` | All paths owned by `@Alpaq92` |
| `.github/workflows/ci.yml` | `swift build` / `swift test`, `xcodebuild` for iOS Simulator, `pod lib lint` |
| `.github/workflows/codeql.yml` | CodeQL `security-and-quality` query suite on Swift, weekly + per-PR |
| `.github/workflows/security.yml` | gitleaks (secret detection), `dependency-review-action` (PR only), Trivy filesystem scan to SARIF |
| `.github/workflows/auto-merge.yml` | Polls open PRs every 6 h (and on each review / gating-workflow completion) and squash-merges any that meet all eligibility criteria |
| `.github/workflows/changelog.yml` | On every PR merged into `main`, prepends a bullet under `## [Unreleased]` in `CHANGELOG.md`. Commits as `github-actions[bot]` with `[skip ci]` |
| `.github/workflows/release.yml` | Builds + tests on every push to main, packages a tarball + xcframework, publishes a GitHub Release on `v*.*.*` tags. The xcframework is produced by [`segment-integrations/swift-create-xcframework`](https://github.com/segment-integrations/swift-create-xcframework) (pinned to commit `33079d3`); a post-build step injects `FlagHub_FlagHub.bundle` (the SPM resource target) into each framework slice so the binary distribution has working flag artwork |
| `.github/workflows/sync-upstream.yml` | Daily cron (02:17 UTC) that fetches `madebybowtie/FlagKit` master, opens or refreshes a `sync/upstream-flagkit` PR when we're behind. Opens a conflict-labelled issue if the merge can't auto-resolve |
| `.github/dependabot.yml` | Weekly version-update PRs for the `github-actions` and `swift` ecosystems, Mondays 06:00 UTC, conventional-commits prefixes (`ci:`, `build:`) |

## Required one-time setup

These cannot be configured via committed files — do them in the GitHub UI / via `gh`.

### 1. Install CodeRabbit

Visit <https://github.com/apps/coderabbitai> and install on the repo. The committed `.coderabbit.yaml` is picked up automatically.

### 2. Branch protection

Settings → Branches → Add rule for `main` (and any other protected branch):

- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
  - Required: `CI / spm-build`, `CodeQL / analyze`, `Security / secret-scan`, `Security / dependency-review`, `Security / trivy`
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings — leave **disabled** so admins can still bypass via the merge UI
- ✅ Allow auto-merge

Or via gh:

```sh
gh api -X PUT repos/<owner>/<repo>/branches/main/protection \
  -F required_pull_request_reviews.required_approving_review_count=1 \
  -F required_status_checks.strict=true \
  -F required_status_checks.contexts[]='CI / spm-build' \
  -F required_status_checks.contexts[]='CodeQL / analyze' \
  -F required_status_checks.contexts[]='Security / secret-scan' \
  -F enforce_admins=false \
  -F allow_force_pushes=false \
  -F allow_deletions=false
```

### 3. Enable auto-merge in repo settings

Settings → General → Pull Requests → ✅ Allow auto-merge.

### 4. Optional secrets

| Secret | Used by | Purpose |
|---|---|---|
| `COCOAPODS_TRUNK_TOKEN` | (none yet) | Add `pod trunk push` step to `release.yml` if you want to publish to the CocoaPods trunk on tag |

## How to bypass auto-merge

Anyone with merge permission on the branch can merge manually via the GitHub PR UI at any time. The auto-merge workflow only adds eligible PRs to the merge queue — it does not block manual merges. Specifically:

- **Admin override** — repo admins always have the **Merge pull request** button available regardless of branch protection (provided `enforce_admins=false` above).
- **Skip the wait** — admins can merge before the 7-day window elapses.
- **Manually trigger** — run `auto-merge.yml` via the **workflow_dispatch** input (`pr_number=NNN`) to evaluate a specific PR right now instead of waiting for the next 6-hourly tick.

## Eligibility criteria (auto-merge)

A PR is auto-merged only when **all** of these hold:

1. Not a draft
2. **Approval** — one of:
   - PR author is `dependabot[bot]` (the bot is the author-of-trust; no separate human review needed for routine dependency bumps), OR
   - at least one **APPROVED** review whose author is in `.github/CODEOWNERS`, a repo collaborator, or `coderabbitai[bot]`
3. **Soak window**:
   - Dependabot-authored PRs: **none** — merge as soon as everything else is green
   - All other PRs: the eligible approval is ≥ 7 days old (measured from the latest qualifying `APPROVED` review's `submitted_at`)
4. No open **CHANGES_REQUESTED** review (latest-per-reviewer wins) — this still blocks Dependabot PRs if someone explicitly requests changes
5. Every check run on the head SHA has `conclusion = success` (no failure, cancelled, timed-out, or pending)
6. PR is mergeable (no conflicts)

Merge strategy is **squash**.

### When evaluation happens

The workflow re-evaluates the eligible PR set on each of:

- The scheduled tick (every 6 hours at xx:23 UTC)
- Any `pull_request_review` submission
- Any `workflow_run.completed` event from the `CI`, `Build & Release`, `CodeQL`, or `Security` workflows
- `workflow_dispatch` (optionally with a `pr_number` input to evaluate a specific PR)

The `workflow_run` triggers are what give Dependabot PRs their "merge within minutes of CI green" behaviour without polling.

## Upstream sync

`.github/workflows/sync-upstream.yml` runs daily at 02:17 UTC (and on `workflow_dispatch`). It:

1. Fetches `madebybowtie/FlagKit` `master`.
2. Computes how many commits our `main` is behind upstream.
3. If behind > 0:
   - **Clean merge** → force-pushes the merge onto the `sync/upstream-flagkit` branch and opens (or refreshes) a PR titled `chore(sync): merge N commit(s) from upstream FlagKit master`, labelled `upstream-sync` + `dependencies`. The PR body lists every commit being merged.
   - **Conflict** → opens an `upstream-sync` + `conflict`-labelled issue with manual-resolution instructions.

The sync PR's author is `github-actions[bot]`, **not** `dependabot[bot]`, so it does **not** get the Dependabot zero-soak fast-path. It goes through the standard 7-day-from-approval review window — appropriate, because upstream changes can carry breaking API or asset modifications worth eyeballing.

### Workflows don't trigger workflows by default

The default `GITHUB_TOKEN` doesn't trigger downstream workflows on PRs it opens (GitHub's anti-loop policy). Out of the box the sync PR opens but CI / CodeQL / Security stay idle. To wire that up, create a PAT with `repo` scope and add it as the repo secret `SYNC_PAT`; the workflow's `checkout` and `gh` steps both prefer `secrets.SYNC_PAT` over `secrets.GITHUB_TOKEN`. Without it, dispatch CI manually via the PR's *Re-run jobs* button.
