# FlagHub — overview

This document is the deep dive. The repo's [README](../README.md) is the elevator pitch; everything else lives here or in the sibling docs.

## Table of contents

1. [What this is](#what-this-is)
2. [How it differs from upstream](#how-it-differs-from-upstream)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Project layout](#project-layout)
6. [Helper scripts](#helper-scripts)
7. [GitHub automation](#github-automation)
8. [Changelog](#changelog)
9. [Maintenance notes](#maintenance-notes)
10. [License](#license)

---

## What this is

FlagHub is a fork of [madebybowtie/FlagKit](https://github.com/madebybowtie/FlagKit) — the Apple-platforms flag-icon library. Upstream has been dormant since 2020 with a stack of stale PRs and unanswered issues. This fork:

- Merges every open upstream PR
- Fixes infrastructure / packaging / SVG-hygiene issues without touching the flag artwork itself
- Adds two Swift API conveniences (`Flag.all`, SwiftUI `Image(flag:)`)
- Optimises every PNG losslessly (~42 % smaller)
- Sets up the GitHub-side automation (review, security, auto-merge, release)

The flag artwork is intentionally identical to upstream — no hand-drawn replacements ship here. See [FORK.md](../FORK.md) for the full audit trail including what was attempted and reverted.

---

## How it differs from upstream

### Merged pull requests (all seven open ones)

| PR | Subject |
|---|---|
| [#65](https://github.com/madebybowtie/FlagKit/pull/65) | `Flag.emoji` accessor |
| [#79](https://github.com/madebybowtie/FlagKit/pull/79) | updated podspec |
| [#82](https://github.com/madebybowtie/FlagKit/pull/82) | ZA flag sizing fix |
| [#100](https://github.com/madebybowtie/FlagKit/pull/100) | `resource` → `resource_bundle` migration |
| [#107](https://github.com/madebybowtie/FlagKit/pull/107) | visionOS support |
| [#109](https://github.com/madebybowtie/FlagKit/pull/109) | updated SY flag (free-Syria green) |
| [#110](https://github.com/madebybowtie/FlagKit/pull/110) | updated IR flag (Lion and Sun) |

### Resolved issues

| Issue | Subject |
|---|---|
| [#66](https://github.com/madebybowtie/FlagKit/issues/66) | SVG element IDs scoped per file (prevents cross-document gradient bleeding when multiple flags share a DOM) |
| [#91](https://github.com/madebybowtie/FlagKit/issues/91) | CH and VA squared (15 × 15) |
| [#92](https://github.com/madebybowtie/FlagKit/issues/92) | `Flag.all` / `Flag.supportedCountryCodes` |
| [#93](https://github.com/madebybowtie/FlagKit/issues/93) | SwiftUI `Image(flag:)` initialisers |
| [#95](https://github.com/madebybowtie/FlagKit/issues/95) | WW (world / default) flag restored |
| [#98](https://github.com/madebybowtie/FlagKit/issues/98) | broken README sample-project link |
| [#106](https://github.com/madebybowtie/FlagKit/issues/106) | every SVG carries an MIT attribution header |

### Infrastructure

- Every PNG recompressed losslessly with `oxipng -o 6` (1281 files, ~983 KiB saved, 41.7 %).
- Header banner rebranded to "FlagHub 3.0".
- Podspec attribute fixed (`s.resource_bundle = ...` ← invalid → `s.resources = ...`).
- `.gitignore` expanded for Python tooling, Windows, Linux, IDE artefacts.

### Reverted / deferred

- **Tier 2 visual corrections** (AL eagle, CN stars, MD coat of arms, US 13-stripe / 50-star canton, ZW Hungwe bird) were prototyped and reverted — the hand-drawn artwork didn't meet the polish bar of upstream's professional vector set.
- **Tier 3 new flags** (AC, AQ, BQ, CP, DG, EA, EH, IC, TA) — same reason, same outcome. The commits remain in branch history for anyone wanting to redo them with a real vector illustrator.

Full reasoning + commit-hash audit trail: [FORK.md](../FORK.md).

---

## Installation

### Swift Package Manager (recommended)

```swift
.package(url: "https://github.com/<owner>/FlagHub.git", branch: "main")
```

or the upstream URL if you only want the PR-merged subset:

```swift
.package(url: "https://github.com/madebybowtie/FlagKit.git", from: "2.5.0")
```

### Carthage

```
github "madebybowtie/FlagKit"
```

### CocoaPods

```ruby
pod 'FlagKit'
```

### Manual

Drop `Sources/FlagKit/FlagKit.xcassets` into your Xcode target.

---

## Usage

### Look up a flag

```swift
let countryCode = Locale.current.regionCode!
let flag = Flag(countryCode: countryCode)!

let originalImage = flag.originalImage            // unstyled
let styledImage   = flag.image(style: .circle)    // iOS / tvOS / visionOS only
```

Styles: `.none`, `.roundedRect`, `.square`, `.circle`. Styling is not available on macOS — use `originalImage` and clip in your view layer.

### Emoji

```swift
Flag(countryCode: "JP")?.emoji  // "🇯🇵"
```

### Enumerate every flag

```swift
Flag.supportedCountryCodes  // ["AD", "AE", "AF", … 256 entries …]
Flag.all                    // [Flag, Flag, Flag, …]
```

The list is mostly ISO 3166-1 alpha-2, with these additions: `EU`, `WW`, `LGBT`, `GB-ENG`, `GB-NIR`, `GB-SCT`, `GB-WLS`, `GB-ZET`, `US-CA`.

### SwiftUI

```swift
import SwiftUI
import FlagKit

struct CountryCell: View {
    let countryCode: String
    var body: some View {
        Image(flagWithCountryCode: countryCode)?
            .resizable()
            .interpolation(.high)
            .aspectRatio(contentMode: .fit)
            .frame(width: 32)
    }
}
```

Add `.interpolation(.high)` and `.resizable()` when rendering larger than the asset's native pixel size — FlagHub still ships raster PNGs, not PDFs, so SwiftUI's default `Image` scaling can soften the result. See [issue #93](https://github.com/madebybowtie/FlagKit/issues/93).

Alternative initialisers:

```swift
Image(flag: flagInstance)                                   // non-failable, takes a Flag
Image(flagWithCountryCode: "PL")                            // failable
Image(flagWithCountryCode: "PL", style: .circle)            // failable, styled (iOS/tvOS/visionOS only)
```

### Direct bundle access

```swift
let bundle = FlagKit.assetBundle
let originalImage = UIImage(named: countryCode, in: bundle, compatibleWith: nil)
```

---

## Project layout

```text
FlagHub/
├── Assets/
│   ├── PNG/                   # 768 standalone PNG files (1x/2x/3x for each flag)
│   ├── SVG/                   # 255 SVG sources (every flag except WW)
│   └── Flags.md               # alphabetical table of every supported flag
├── Sources/
│   ├── FlagKit/               # the Swift Package target
│   │   ├── Flag.swift             # core Flag class + emoji + style
│   │   ├── FlagCodes.swift        # Flag.all / Flag.supportedCountryCodes (#92)
│   │   ├── FlagKit.swift          # bundle accessor
│   │   ├── FlagStyle.swift        # rounded / square / circle
│   │   ├── NSImage.swift          # macOS extension
│   │   ├── SwiftUI.swift          # Image(flag:) initialisers (#93)
│   │   ├── UIImage.swift          # iOS / tvOS / visionOS extension
│   │   ├── FlagKit.h              # ObjC umbrella
│   │   ├── FlagKit.xcassets/      # asset catalogue, one imageset per code
│   │   ├── FlagKitFramework.xcconfig
│   │   └── Info.plist
│   ├── FlagKitDemo-iOS/       # demo app (Xcode project only, not part of SPM target)
│   ├── FlagKitTests/          # XCTest target
│   └── FlagKit.xcodeproj/     # Xcode project for framework + demo + tests
├── scripts/                   # Python helpers (see below)
├── docs/
│   └── OVERVIEW.md            # this file
├── .github/
│   ├── CODEOWNERS
│   ├── README.md              # GitHub automation diagram + setup
│   └── workflows/             # CI / CodeQL / security / auto-merge / release
├── .coderabbit.yaml           # CodeRabbit profile
├── FlagKit.podspec
├── FORK.md                    # full change-log including reverted work
├── LICENSE                    # MIT (Bowtie AB + Alpaq92)
├── Package.swift              # Swift Package Manager manifest
├── README.md                  # short pitch
└── header.png                 # title banner
```

---

## Helper scripts

All under `scripts/`. They use only Python ≥ 3.10 and one optional dependency (`pyoxipng` for the optimiser). Every script is idempotent — running it on a clean tree is a no-op.

| Script | What it does |
|---|---|
| `scripts/scope_svg_ids.py` | Prefixes every `id="X"` in each SVG with the country code (e.g. `id="linearGradient-1"` → `id="AR_linearGradient-1"`), and rewrites every `url(#X)`, `href="#X"`, and `xlink:href="#X"` reference to match. Fixes [#66](https://github.com/madebybowtie/FlagKit/issues/66) where the same gradient id could resolve to a different flag when both were inlined in the same DOM. |
| `scripts/add_svg_attribution.py` | Prepends a standard MIT attribution comment to every SVG: source = FlagHub (fork of FlagKit by Bowtie), upstream URL, license = MIT. Country name pulled from `Assets/Flags.md`. Fixes [#106](https://github.com/madebybowtie/FlagKit/issues/106). |
| `scripts/optimize_pngs.py` | Runs `oxipng -o 6` (level 6, lossless) over every PNG in `Assets/PNG/`, `Sources/FlagKit/FlagKit.xcassets/**/*.png`, and `header.png`. Requires `pip install pyoxipng`. |

Re-run them after any asset edit:

```sh
python scripts/scope_svg_ids.py        # if you added or edited an SVG
python scripts/add_svg_attribution.py  # if you added a new SVG
python scripts/optimize_pngs.py        # if you added or replaced a PNG
```

---

## GitHub automation

The full PR-to-deploy pipeline is documented in [`.github/README.md`](../.github/README.md). Quick summary:

- **Reviews** — CodeRabbit auto-reviews every PR (`.coderabbit.yaml`).
- **Build / test** — `swift build`, `swift test`, `xcodebuild` for iOS Simulator, `pod lib lint` on every PR + push (`.github/workflows/ci.yml`).
- **Security** — CodeQL `security-and-quality` queries on Swift (`codeql.yml`), gitleaks for secrets + dependency-review-action + Trivy filesystem scan (`security.yml`).
- **Auto-merge** — any PR that's at least 7 days old, has an `APPROVED` review by a code owner / collaborator / `coderabbitai[bot]`, and has every check green is squash-merged automatically. Workflow runs every 6 hours and on every review event (`auto-merge.yml`).
- **Changelog** — `changelog.yml` listens for `pull_request: closed (merged)` and prepends a one-line entry under `## [Unreleased]` in [CHANGELOG.md](../CHANGELOG.md), committing back with `[skip ci]` so it doesn't loop.
- **Release** — every push to main rebuilds the SPM target and xcframework, uploads a tarball as a workflow artefact, and on `v*.*.*` tags also publishes a GitHub Release (`release.yml`).

You can always **bypass** by clicking *Merge pull request* in the UI — the auto-merge workflow only enables eligible PRs, it doesn't block manual merges. Branch protection is configured with `enforce_admins=false` so the repo owner keeps the merge button.

A standalone copy of the same documentation is also in `C:\Users\Alpaq\Documents\github-pr-automation-setup.md` for reuse on other projects.

---

## Changelog

The repo carries a [CHANGELOG.md](../CHANGELOG.md) in Keep-a-Changelog format. The `[Unreleased]` section is **auto-populated** by `.github/workflows/changelog.yml`:

- Trigger: `pull_request: closed` on `main` / `master` with `merged == true`.
- For each merged PR, prepends a Markdown bullet:

  ```text
  - [#<number>](<pr-url>) <pr-title> — @<author>
    > <first non-blank line of the PR body, capped at 200 chars>
  ```

- Idempotent: if `[#<number>]` is already in the Unreleased section the workflow exits without committing.
- The bot commit is signed by `github-actions[bot]` and ends with `[skip ci]` so neither the CI, auto-merge, nor release workflows re-trigger on it.

At release time, rename the `## [Unreleased]` heading to `## [X.Y.Z] - YYYY-MM-DD`, add a fresh empty `## [Unreleased]` block above it, and tag the commit `vX.Y.Z`. The release workflow then publishes the GitHub Release using the Markdown between those two headings as the release notes.

---

## Maintenance notes

### Adding a new flag (no rasterizer locally — recommended)

1. Drop the new SVG into `Assets/SVG/` (uppercase ISO code, e.g. `AC.svg`).
2. Add an entry in `Assets/Flags.md` (alphabetically; bump the header count).
3. Add the code to `Flag.supportedCountryCodes` in `Sources/FlagKit/FlagCodes.swift` (alphabetical).
4. Run `python scripts/scope_svg_ids.py && python scripts/add_svg_attribution.py`.
5. On a macOS box, rasterize the SVG to `Assets/PNG/<CODE>.png`, `<CODE>@2x.png`, `<CODE>@3x.png` (21 × 15, 42 × 30, 63 × 45 — or 15 × 15 / 30 × 30 / 45 × 45 if the official flag is square). Create the matching `Sources/FlagKit/FlagKit.xcassets/<CODE>.imageset/` with `Contents.json` (no `1x` filename, just `@2x` and `@3x` per the post-#100 convention) and the rasterized `@2x.png` / `@3x.png`.
6. Re-run `python scripts/optimize_pngs.py`.
7. Commit, open a PR, let CodeRabbit + CI + auto-merge handle it.

### Editing an existing flag

Same steps 4–7 above after editing the SVG.

### Cutting a release

```sh
git tag v3.0.0
git push origin v3.0.0
```

`release.yml` picks up the tag, builds, creates the GitHub Release with auto-generated notes and the framework tarball attached. If you've configured `COCOAPODS_TRUNK_TOKEN`, add a step that does `pod trunk push FlagKit.podspec` after the release artefact is uploaded.

### Reverting an asset

`Assets/SVG/<CODE>.svg` and the corresponding xcassets imageset are independent of the Swift target — `git checkout <ref> -- Assets/SVG/<CODE>.svg Sources/FlagKit/FlagKit.xcassets/<CODE>.imageset/` is safe at any time. Re-run the two SVG scripts afterwards so the file picks up the fork's id-scoping and attribution comment.

---

## License

FlagHub inherits FlagKit's MIT license:

```
Copyright (c) 2016 Bowtie AB
Copyright (c) 2026 Alpaq92
```

See [LICENSE](../LICENSE).
