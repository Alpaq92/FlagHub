# Repository automation

This directory configures the GitHub-side workflow for FlagHub: PR reviews, security scanning, conditional auto-merge, and rebuild + release on every merge.

## Overview

```mermaid
flowchart TD
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
```

## Files

| Path | Purpose |
|---|---|
| `.coderabbit.yaml` | CodeRabbit profile. Auto-reviews every PR, skips image assets, runs LanguageTool + markdownlint + shellcheck |
| `.github/CODEOWNERS` | All paths owned by `@Alpaq92` |
| `.github/workflows/ci.yml` | `swift build` / `swift test`, `xcodebuild` for iOS Simulator, `pod lib lint` |
| `.github/workflows/codeql.yml` | CodeQL `security-and-quality` query suite on Swift, weekly + per-PR |
| `.github/workflows/security.yml` | gitleaks (secret detection), `dependency-review-action` (PR only), Trivy filesystem scan to SARIF |
| `.github/workflows/auto-merge.yml` | Polls open PRs every 6 h (and on each review) and squash-merges any that meet all eligibility criteria |
| `.github/workflows/release.yml` | Builds + tests on every push to main, packages a tarball, publishes a GitHub Release on `v*.*.*` tags |

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
3. The eligible **approval is ≥ 7 days old** (measured from the latest qualifying `APPROVED` review's `submitted_at`). For Dependabot PRs the timer effectively starts at PR creation since there is no separate approval moment
4. No open **CHANGES_REQUESTED** review (latest-per-reviewer wins) — this still blocks Dependabot PRs if someone explicitly requests changes
5. Every check run on the head SHA has `conclusion = success` (no failure, cancelled, timed-out, or pending)
6. PR is mergeable (no conflicts)

Merge strategy is **squash**.
