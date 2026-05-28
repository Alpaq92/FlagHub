# Changelog

All notable changes to FlagHub.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/).

Entries under `[Unreleased]` are appended automatically by `.github/workflows/changelog.yml` when a PR is merged into `main`. Rename `[Unreleased]` → `[X.Y.Z] - YYYY-MM-DD` at release time (the release workflow can also do this).

## [Unreleased]

<!-- Auto-generated entries are inserted directly below this line by the changelog workflow. Do not delete the heading or the comment - the workflow looks for them. -->

## [3.0.0] - 2026-05-28

Initial fork-flagkit release. See [docs/OVERVIEW.md](docs/OVERVIEW.md) for the full audit trail.

### Merged
- All seven open upstream pull requests ([#65](https://github.com/madebybowtie/FlagKit/pull/65), [#79](https://github.com/madebybowtie/FlagKit/pull/79), [#82](https://github.com/madebybowtie/FlagKit/pull/82), [#100](https://github.com/madebybowtie/FlagKit/pull/100), [#107](https://github.com/madebybowtie/FlagKit/pull/107), [#109](https://github.com/madebybowtie/FlagKit/pull/109), [#110](https://github.com/madebybowtie/FlagKit/pull/110))

### Fixed
- SVG element IDs are scoped per file to prevent cross-document `url(#…)` collisions ([#66](https://github.com/madebybowtie/FlagKit/issues/66))
- CH and VA are now square (15 × 15) ([#91](https://github.com/madebybowtie/FlagKit/issues/91))
- WW (world / default) flag restored from upstream pre-2.0 history ([#95](https://github.com/madebybowtie/FlagKit/issues/95))
- Broken sample-project link removed from README ([#98](https://github.com/madebybowtie/FlagKit/issues/98))
- `FlagHub.podspec` uses the correct `s.resources` attribute (PR #100's `s.resource_bundle` was invalid DSL and would have silently dropped the asset catalog at `pod install` time)

### Added
- `Flag.all` and `Flag.supportedCountryCodes` ([#92](https://github.com/madebybowtie/FlagKit/issues/92))
- SwiftUI `Image(flag:)`, `Image(flagWithCountryCode:)`, `Image(flagWithCountryCode:style:)` ([#93](https://github.com/madebybowtie/FlagKit/issues/93))
- MIT attribution comment on every SVG ([#106](https://github.com/madebybowtie/FlagKit/issues/106))
- GitHub Actions pipeline: CI, CodeQL, gitleaks + dependency-review + Trivy security, auto-merge after 7 days with code-owner / collaborator / CodeRabbit approval, release build with xcframework on push to main and GitHub Release on `v*.*.*` tags
- CodeRabbit config (`.coderabbit.yaml`), CODEOWNERS

### Changed
- Every PNG in the repo losslessly recompressed with `oxipng -o 6` (2.3 MiB → 1.4 MiB, –41.7 %)
- Title banner rebranded to "FlagHub 3.0" with a soft white glow for dark-mode legibility
- `LICENSE` now carries an additional `Copyright (c) 2026 Alpaq92` line; original Bowtie AB notice preserved
- `.gitignore` expanded for Python tooling (`scripts/`), Windows, Linux, IDE artefacts
- README slimmed to a quick pitch; full project state in [docs/OVERVIEW.md](docs/OVERVIEW.md)

[Unreleased]: https://github.com/Alpaq92/FlagHub/compare/v3.0.0...HEAD
[3.0.0]: https://github.com/Alpaq92/FlagHub/releases/tag/v3.0.0
