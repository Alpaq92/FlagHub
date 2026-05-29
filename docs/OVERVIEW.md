# FlagHub — overview

The deep dive. The [README](../README.md) is the elevator pitch; everything else lives here.

## Table of contents

1. [What this is](#what-this-is)
2. [Upstream PRs merged](#upstream-prs-merged)
3. [Upstream issues resolved](#upstream-issues-resolved)
4. [What was not done, and why](#what-was-not-done-and-why)
5. [PNG optimization](#png-optimization)
6. [Icon](#icon)
7. [Installation](#installation)
8. [Usage](#usage)
9. [Project layout](#project-layout)
10. [Helper scripts](#helper-scripts)
11. [GitHub automation](#github-automation)
12. [Changelog](#changelog)
13. [Maintenance notes](#maintenance-notes)
14. [License](#license)

---

## What this is

FlagHub is a fork of [madebybowtie/FlagKit](https://github.com/madebybowtie/FlagKit) — the Apple-platforms flag-icon library. Upstream has been dormant since 2020 with stalled PRs and unanswered issues. This fork:

- Merges every open upstream PR
- Fixes infrastructure / packaging / SVG-hygiene issues without touching the flag artwork itself
- Adds two Swift API conveniences (`Flag.all`, SwiftUI `Image(flag:)`)
- Losslessly recompresses every PNG (≈42 % smaller)
- Sets up the GitHub-side automation (review, security, auto-merge, changelog, release)

The flag artwork is intentionally identical to upstream — no hand-drawn replacements ship here. The Tier 2 (existing-flag corrections) and Tier 3 (nine new flag codes) work was prototyped and reverted because the hand-drawn output did not meet the polish bar of upstream's vector set. Commits remain in branch history.

---

## Upstream PRs merged

All seven open pull requests on upstream were fast-forwarded onto this fork. Conflicts were resolved in favour of the fork's working state (see each commit message for the exact call):

| Upstream PR | Title | Notes |
|---|---|---|
| [#65](https://github.com/madebybowtie/FlagKit/pull/65) | Add `Flag.emoji` accessor | Clean merge |
| [#79](https://github.com/madebybowtie/FlagKit/pull/79) | Update `FlagHub.podspec` | Conflict in `swift_versions` — kept the newer list (5.0–5.3) from master; PR was stale |
| [#82](https://github.com/madebybowtie/FlagKit/pull/82) | Fix sizing of ZA flags | Clean merge |
| [#100](https://github.com/madebybowtie/FlagKit/pull/100) | Migrate `resource` → `resource_bundle` | Clean merge (the podspec attribute key itself was wrong DSL — fixed separately, see Infrastructure below) |
| [#107](https://github.com/madebybowtie/FlagKit/pull/107) | Add visionOS support | Conflict in `Flag.swift` — kept #65's emoji block alongside #107's `os(visionOS)` guard |
| [#109](https://github.com/madebybowtie/FlagKit/pull/109) | Update SY flag (free-Syria green) | Clean merge |
| [#110](https://github.com/madebybowtie/FlagKit/pull/110) | Update IR flag (Lion and Sun) | Conflict on `IR.imageset/IR.png` — dropped the 1x PNG, consistent with PR #100's removal of 1x PNGs from xcassets; kept the new @2x/@3x |

---

## Upstream issues resolved

### Tier 1 — bug fixes and infrastructure

| Issue | Subject | Resolution |
|---|---|---|
| [#66](https://github.com/madebybowtie/FlagKit/issues/66) | SVG gradient IDs collide across files | Scoped 2,645 element IDs and rewrote 1,462 references across all 255 SVGs; helper at `scripts/scope_svg_ids.py` is idempotent |
| [#91](https://github.com/madebybowtie/FlagKit/issues/91) | CH and VA should be square | Both SVGs re-aspected to 15 × 15 via centred `viewBox` crop |
| [#95](https://github.com/madebybowtie/FlagKit/issues/95) | WW (default world) flag removed in 2.0 | Restored from the parent of `a7b7d9e` into `Assets/PNG/` and the xcassets imageset |
| [#98](https://github.com/madebybowtie/FlagKit/issues/98) | Broken README sample-project link | Removed (the target path never existed in any history) |
| [#106](https://github.com/madebybowtie/FlagKit/issues/106) | Add MIT attribution comments to each SVG | Prepended to all 256 SVGs; helper at `scripts/add_svg_attribution.py` is idempotent |

### Tier 2 — single-flag visual corrections (reverted)

Issues [#62](https://github.com/madebybowtie/FlagKit/issues/62) (CN stars), [#70](https://github.com/madebybowtie/FlagKit/issues/70) (MD coat of arms), [#76](https://github.com/madebybowtie/FlagKit/issues/76) (US 15 stripes / 18 dots), [#96](https://github.com/madebybowtie/FlagKit/issues/96) (ZW missing Hungwe bird), and [#104](https://github.com/madebybowtie/FlagKit/issues/104) (AL eagle and red) all flag genuine defects in the upstream artwork. Hand-drawn corrections for each were prototyped and **reverted** — the replacement artwork did not meet the quality bar of the rest of the upstream set. The pure-geometry pieces (US stripe count, CN star positions per the 1949 construction sheet) were correct as math but still hand-edited SVGs which is hard to justify next to professional vector artwork. Fixing these flags properly needs a vector illustrator. The commits remain in branch history.

### Tier 3 — missing flags (partial — 5 of 9 added)

Issues [#36](https://github.com/madebybowtie/FlagKit/issues/36), [#73](https://github.com/madebybowtie/FlagKit/issues/73), [#83](https://github.com/madebybowtie/FlagKit/issues/83), [#84](https://github.com/madebybowtie/FlagKit/issues/84), [#97](https://github.com/madebybowtie/FlagKit/issues/97), [#101](https://github.com/madebybowtie/FlagKit/issues/101) collectively requested AC, AQ, BQ, CP, DG, EA, EH, IC, TA. The first attempt was hand-drawn approximations; those were **reverted** because the silhouettes did not meet upstream's quality bar.

**Five of the nine were subsequently ported from [`murgupluoglu/flagkit-android`](https://github.com/murgupluoglu/flagkit-android)** (MIT) — a hand-authored vector flag library that ships several codes upstream FlagKit lacks. The Android `VectorDrawable` XML maps mechanically to SVG (`pathData` → `d`, `fillColor` → `fill`, `fillType="evenOdd"` → `fill-rule="evenodd"`, group transforms map directly); the converter lives at `scripts/port_flags_from_android.py` and is reproducible. Ported codes:

| Code | Country / region | Source detail |
|---|---|---|
| AQ | Antarctica | UN-style 2002 design — blue with white continental silhouette |
| BQ | Bonaire, Sint Eustatius and Saba | Yellow/blue/white tri-triangle with red compass star |
| DG | Diego Garcia (BIOT) | Union Jack canton, wavy stripes, palm tree, St. Edward's crown |
| EH | Western Sahara | SADR — red triangle, black/white/green stripes, red star + crescent |
| IC | Canary Islands | Simplified tricolor (white / blue / yellow); coat of arms omitted, matching the murgupluoglu source |

Total ships now: **260 flags**. (Net change vs. upstream: +5 from `flagkit-android`, −1 from dropping the Pride flag — see [Scope](#scope) — yielding 260.) The remaining four Tier-3 codes — **AC** (Ascension Island), **CP** (Clipperton Island), **EA** (Ceuta + Melilla), **TA** (Tristan da Cunha) — are not in `flagkit-android` either and are still missing. Hand-drawn prototypes for those remain reverted; commits are in branch history.

### Scope

FlagHub ships **geo-political flags only** — sovereign-state, dependency, sub-national, and intergovernmental (EU, WW). Codes that upstream FlagKit shipped which fall outside that scope have been removed in this fork; consumers who need such artwork can pull it from upstream FlagKit directly or supply their own asset.

### Tier 4 — code features

| Issue | Subject | Resolution |
|---|---|---|
| [#81](https://github.com/madebybowtie/FlagKit/issues/81) | Swift Package Manager support | **Already done upstream** — `Package.swift` at repo root, kept as-is |
| [#92](https://github.com/madebybowtie/FlagKit/issues/92) | "Get all flags in one call" | Added `Flag.supportedCountryCodes: [String]` and `Flag.all: [Flag]` in `Sources/FlagHub/FlagCodes.swift` |
| [#93](https://github.com/madebybowtie/FlagKit/issues/93) | Pixelated images in SwiftUI | Added `Image(flag:)`, `Image(flagWithCountryCode:)`, `Image(flagWithCountryCode:style:)` in `Sources/FlagHub/SwiftUI.swift`. The root cause (raster-only PNG assets) is not fully solved, but the docs now point consumers at `.interpolation(.high)` and `.resizable()` for sharper SwiftUI rendering |

### Infrastructure

- Every PNG losslessly recompressed with `oxipng -o 6` — see [PNG optimization](#png-optimization).
- Header banner rebranded to "FlagHub 3.0" with a soft white glow for dark-mode legibility.
- `FlagHub.podspec` attribute fixed: PR #100's `s.resource_bundle = ...` (singular, invalid CocoaPods DSL) → `s.resources = ...` (would have silently dropped the asset catalog at `pod install` time).
- `.gitignore` expanded for Python tooling (`scripts/`), Windows, Linux, and IDE artefacts.
- `LICENSE` carries `Copyright (c) 2026 Alpaq92` alongside the upstream `Copyright (c) 2016 Bowtie AB` notice.

---

## What was not done, and why

### PNG regeneration for the squared CH and VA SVGs

The Tier 1 viewBox crop on `CH.svg` and `VA.svg` was applied to the SVGs but the corresponding `Assets/PNG/CH*.png`, `VA*.png` and in-bundle xcassets PNGs still encode the old 21 × 15 aspect ratio. No SVG → PNG rasterizer was available in this environment (`ImageMagick`, `Inkscape`, `rsvg-convert`, `cairosvg` are all missing). To finish locally, regenerate the six affected PNGs from the updated SVGs at 15 × 15, 30 × 30, and 45 × 45.

This is the only outstanding PNG regen — Tier 2 SVG changes that would have needed re-rasterising were reverted.

### Four still-missing ISO codes (Tier 3 remainder)

After porting AQ, BQ, DG, EH, IC from `flagkit-android` (see Tier 3 above), the codes **AC, CP, EA, TA** are still unsupported because neither upstream FlagKit nor `flagkit-android` ship them. Adding these properly requires a vector illustrator (Sketch / Illustrator / Affinity / Inkscape) and ideally public-domain reference SVGs — out of scope for raw-XML editing.

### Heraldic-accuracy redraws of the complex emblems

Affected: the same set covered in the Tier 2 revert (AL eagle, MD coat of arms, ZW Hungwe bird, CN star geometry, US stripes-and-stars). The reworked SVGs were hand-written silhouettes built from primitives and bezier curves; they read as "the right idea" at typical UI sizes but are not heraldically accurate at large render sizes. Producing renderings at upstream's polish requires real vector tooling and ideally a public-domain reference SVG.

### Remaining upstream issues left untouched

| Issue | Subject | Why not |
|---|---|---|
| [#89](https://github.com/madebybowtie/FlagKit/issues/89) | Port to Android | Different codebase entirely; out of scope for a Swift Package |
| [#94](https://github.com/madebybowtie/FlagKit/issues/94) | Expose SVGs to consumers | Requires bundling `Assets/SVG/` into the `resource_bundle` and adding a `Flag.svgData` / `Flag.svgURL` accessor. Mechanical follow-up — not done in this round |
| [#99](https://github.com/madebybowtie/FlagKit/issues/99) | Placeholder "unknown" flags | The restored WW flag (#95) partly addresses this; further "unknown" variants (pirate, question-mark, etc.) are a design judgement call |
| [#102](https://github.com/madebybowtie/FlagKit/issues/102) | Slow compile times | Needs profiling to find the root cause (likely xcassets size). No measurement was taken |
| [#103](https://github.com/madebybowtie/FlagKit/issues/103) | AZ flag not working | No reproduction provided; cannot diagnose without more info from the reporter |
| [#105](https://github.com/madebybowtie/FlagKit/issues/105) | Flags not displaying in web | FlagHub is an Apple-platforms library; issue lacks reproduction or codebase reference |
| [#111](https://github.com/madebybowtie/FlagKit/issues/111) | "Abandoned?" | Meta question; this fork itself is the answer |

---

## PNG optimization

Every raster asset in the repo was losslessly recompressed. The upstream PNGs were exported from Sketch's `sketchtool` and never run through any post-export optimiser, so they carried ~40 % recoverable overhead.

### Tool comparison

| Tool | Type | Reduction on this set | Notes |
|---|---|---|---|
| `pngcrush` | lossless | ~10–20 % | Older, slow, low yield |
| `OptiPNG` | lossless | ~20–30 % | Reference C implementation; single-threaded |
| **`oxipng`** | **lossless** | **~42 %** | Pure-Rust port of OptiPNG; multithreaded; more exhaustive deflate strategy at the same level |
| `pngquant` | lossy (palette) | 50–70 % | Rejected — the subtle top-to-bottom linear gradients in every flag SVG (see `linearGradient` defs) would risk visible banding once quantised to a 256-colour palette |

`oxipng` was chosen as the best fit: lossless (cannot degrade the gradient fidelity that distinguishes FlagKit's flags from generic flag sets) and materially higher yield than the older lossless tools.

### Results

| Path | Files | Before | After | Saved |
|---|---:|---:|---:|---:|
| `Assets/PNG/` | 768 | 1,374 KiB | 798 KiB | 42 % |
| `Sources/FlagHub/FlagHub.xcassets/` | 512 | 882 KiB | 504 KiB | 43 % |
| `header-light.png` / `header-dark.png` | 2 | — | ≈55 KiB each | — |
| **Total** | **1,281** | **2,356 KiB** | **1,373 KiB** | **41.7 %** |

`icon.png` (≈300 KiB after oxipng) was added later in the project lifecycle and isn't included in the totals above; it's regenerated via `scripts/generate_icon.py` rather than hand-edited, and the optimiser picks it up automatically on subsequent runs. See [Icon](#icon) for what it depicts and how to regenerate.

---

## Icon

`icon.png` at the repo root is the package's visual identity — useful in READMEs, presentations, app stores, or anywhere else you want a FlagHub avatar. It is **not** one of the country flags: those live under `Assets/` and `Sources/FlagHub/FlagHub.xcassets/` and are unrelated to this asset.

![icon.png](../icon.png)

Composition (1024 × 1024, RGBA, transparent outside the disc):

- **Plate** — round, white at the top fading to a faint cool grey at the bottom. Subtle glass treatments give it volume rather than reading as a flat shape: a soft top meniscus arc, a top-left edge-refraction highlight, and a bottom-right inner shadow.
- **Globe** — the royal-blue wireframe globe glyph from [icones.pro/en/blue-globe-icon-png-symbol/](https://icones.pro/en/blue-globe-icon-png-symbol/), licensed per [icones.pro/en/icon-license/](https://icones.pro/en/icon-license/). The source PNG is committed at `scripts/globe_source.png` so the build is reproducible without a network fetch.
- **Depth** — a soft drop shadow under the wireframe makes it appear to float above the plate. The strokes themselves are recoloured from solid blue to a top-to-bottom royal-blue → navy gradient, suggesting light falling on a sphere.

### Regenerating

```sh
pip install Pillow numpy pyoxipng
python scripts/generate_icon.py
python -c "import oxipng; oxipng.optimize('icon.png', level=6)"
```

`scripts/generate_icon.py` renders at 4× supersample (4096 × 4096) and downsamples with LANCZOS for clean anti-aliasing on the disc and stroked paths. All composition parameters — palette, sheen alpha, edge-refraction strength, drop-shadow blur, plate/globe radius ratio — are constants at the top of the file; tweak there if you want to iterate without unpicking the compositor.

---

To re-run after editing PNG assets:

```sh
pip install pyoxipng
python scripts/optimize_pngs.py
```

The script is idempotent — running it on an already-optimised tree either does nothing or claws back a few more bytes.

---

## Installation

### Swift Package Manager (recommended)

```swift
.package(url: "https://github.com/Alpaq92/FlagHub.git", branch: "main")
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
pod 'FlagHub'
```

### Manual

Drop `Sources/FlagHub/FlagHub.xcassets` into your Xcode target.

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

The list is mostly ISO 3166-1 alpha-2, with these additions: `EU`, `WW`, `GB-ENG`, `GB-NIR`, `GB-SCT`, `GB-WLS`, `GB-ZET`, `US-CA`.

### SwiftUI

```swift
import SwiftUI
import FlagHub

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
let bundle = FlagHub.assetBundle
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
│   ├── FlagHub/               # the Swift Package target
│   │   ├── Flag.swift             # core Flag class + emoji + style
│   │   ├── FlagCodes.swift        # Flag.all / Flag.supportedCountryCodes (#92)
│   │   ├── FlagHub.swift          # bundle accessor
│   │   ├── FlagStyle.swift        # rounded / square / circle
│   │   ├── NSImage.swift          # macOS extension
│   │   ├── SwiftUI.swift          # Image(flag:) initialisers (#93)
│   │   ├── UIImage.swift          # iOS / tvOS / visionOS extension
│   │   ├── FlagHub.h              # ObjC umbrella
│   │   ├── FlagHub.xcassets/      # asset catalogue, one imageset per code
│   │   ├── FlagHubFramework.xcconfig
│   │   └── Info.plist
│   ├── FlagHubDemo-iOS/       # demo app (Xcode project only, not part of SPM target)
│   ├── FlagHubTests/          # XCTest target
│   └── FlagHub.xcodeproj/     # Xcode project for framework + demo + tests
├── scripts/                   # Python helpers (see below)
├── docs/
│   └── OVERVIEW.md            # this file
├── .github/
│   ├── CODEOWNERS
│   ├── README.md              # GitHub automation diagram + setup
│   └── workflows/             # CI / CodeQL / security / auto-merge / changelog / release
├── .coderabbit.yaml           # CodeRabbit profile
├── CHANGELOG.md
├── FlagHub.podspec
├── LICENSE                    # MIT (Bowtie AB + Alpaq92)
├── Package.swift              # Swift Package Manager manifest
├── README.md                  # short pitch
├── header-light.png           # title banner (black text, for light theme)
├── header-dark.png            # title banner (light text, for dark theme)
└── icon.png                   # package icon (generated by scripts/generate_icon.py)
```

---

## Helper scripts

Python utilities in `scripts/`, all idempotent — running them on a clean tree is a no-op:

| Script | Purpose |
|---|---|
| `scripts/scope_svg_ids.py` | Prefixes every `id="X"` in each SVG with the country code (e.g. `id="linearGradient-1"` → `id="AR_linearGradient-1"`), and rewrites every `url(#X)`, `href="#X"`, and `xlink:href="#X"` reference to match. Fixes [#66](https://github.com/madebybowtie/FlagKit/issues/66) where the same gradient id could resolve to a different flag when both were inlined in the same DOM |
| `scripts/add_svg_attribution.py` | Prepends a standard MIT attribution comment to every SVG: source = FlagHub (fork of FlagKit by Bowtie), upstream URL, license = MIT. Country name pulled from `Assets/Flags.md`. Fixes [#106](https://github.com/madebybowtie/FlagKit/issues/106) |
| `scripts/optimize_pngs.py` | Losslessly recompresses every PNG in the repo with `oxipng -o 6`. Requires `pip install pyoxipng`. See [PNG optimization](#png-optimization) for tool-choice rationale |
| `scripts/generate_icon.py` | Renders `icon.png` at repo root. See [Icon](#icon) for the design rationale, source attribution, and tweakable parameters. Requires Pillow + numpy |
| `scripts/generate_header.py` | Rebuilds `header-light.png` + `header-dark.png` from `scripts/header_source.png` (upstream FlagKit Header.png): wipes the FLAGKIT-2.0 text band, renders "FlagHub 3.0" in Segoe UI Bold + Light at the same cap height, crops to content bbox + a small margin |
| `scripts/port_flags_from_android.py` | Converts the five flag VectorDrawable XMLs in `scripts/vd_src/` (AQ, BQ, DG, EH, IC, sourced from `murgupluoglu/flagkit-android`) to SVG, rasterises at 21×15, 42×30, 63×45, drops files into `Assets/SVG/`, `Assets/PNG/`, and `Sources/FlagHub/FlagHub.xcassets/<CODE>.imageset/`, then patches `Sources/FlagHub/FlagCodes.swift` and `Assets/Flags.md` to register the codes. Idempotent — re-running on an already-ported tree is a no-op. Requires Pillow + PyMuPDF |

Re-run after asset edits:

```sh
python scripts/scope_svg_ids.py            # if you added or edited an SVG
python scripts/add_svg_attribution.py      # if you added a new SVG
python scripts/optimize_pngs.py            # if you added or replaced a PNG
python scripts/port_flags_from_android.py  # if you dropped new VectorDrawable XMLs under scripts/vd_src/
```

---

## GitHub automation

The full PR-to-deploy pipeline is documented in [`AUTOMATION.md`](AUTOMATION.md). Quick summary:

- **Reviews** — CodeRabbit auto-reviews every PR (`.coderabbit.yaml`).
- **Build / test** — `swift build`, `swift test`, `xcodebuild` for iOS Simulator, `pod lib lint` on every PR + push (`.github/workflows/ci.yml`).
- **Security** — CodeQL `security-and-quality` queries on Swift (`codeql.yml`), gitleaks for secrets + dependency-review-action + Trivy filesystem scan (`security.yml`).
- **Auto-merge** — any PR that's at least 7 days old, has an `APPROVED` review by a code owner / collaborator / `coderabbitai[bot]`, and has every check green is squash-merged automatically. Runs every 6 hours and on every review event (`auto-merge.yml`).
- **Changelog** — `changelog.yml` listens for `pull_request: closed (merged)` and prepends a one-line entry under `## [Unreleased]` in [CHANGELOG.md](../CHANGELOG.md), committing back with `[skip ci]` so it doesn't loop.
- **Release** — every push to main rebuilds the SPM target and xcframework, uploads a tarball as a workflow artefact, and on `v*.*.*` tags also publishes a GitHub Release (`release.yml`).
- **Upstream sync** — `sync-upstream.yml` runs daily at 02:17 UTC. Fetches `madebybowtie/FlagKit` master, opens or refreshes a `sync/upstream-flagkit` PR titled `chore(sync): merge N commit(s) from upstream FlagKit master` when we're behind. Falls back to an `upstream-sync` + `conflict`-labelled issue when the merge can't auto-resolve. The PR goes through the normal 7-day-from-approval review window (not the Dependabot zero-soak fast-path).

A standalone copy of the same documentation lives in `C:\Users\Alpaq\Documents\github-pr-automation-setup.md` for reuse on other projects.

---

## Changelog

[CHANGELOG.md](../CHANGELOG.md) is in Keep-a-Changelog format. The `[Unreleased]` section is **auto-populated** by `.github/workflows/changelog.yml`:

- Trigger: `pull_request: closed` on `main` / `master` with `merged == true`.
- For each merged PR it prepends a Markdown bullet:

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
3. Add the code to `Flag.supportedCountryCodes` in `Sources/FlagHub/FlagCodes.swift` (alphabetical).
4. Run `python scripts/scope_svg_ids.py && python scripts/add_svg_attribution.py`.
5. On a macOS box, rasterize the SVG to `Assets/PNG/<CODE>.png`, `<CODE>@2x.png`, `<CODE>@3x.png` (21 × 15, 42 × 30, 63 × 45 — or 15 × 15 / 30 × 30 / 45 × 45 if the official flag is square). Create the matching `Sources/FlagHub/FlagHub.xcassets/<CODE>.imageset/` with `Contents.json` (no `1x` filename, just `@2x` and `@3x` per the post-#100 convention) and the rasterized `@2x.png` / `@3x.png`.
6. Re-run `python scripts/optimize_pngs.py`.
7. Commit, open a PR, let CodeRabbit + CI + auto-merge handle it.

### Editing an existing flag

Same steps 4–7 above after editing the SVG.

### Cutting a release

```sh
git tag v3.0.0
git push origin v3.0.0
```

`release.yml` picks up the tag, builds, creates the GitHub Release with auto-generated notes and the framework tarball attached. If you've configured `COCOAPODS_TRUNK_TOKEN`, add a step that does `pod trunk push FlagHub.podspec` after the release artefact is uploaded.

### Reverting an asset

`Assets/SVG/<CODE>.svg` and the corresponding xcassets imageset are independent of the Swift target — `git checkout <ref> -- Assets/SVG/<CODE>.svg Sources/FlagHub/FlagHub.xcassets/<CODE>.imageset/` is safe at any time. Re-run the two SVG scripts afterwards so the file picks up the fork's id-scoping and attribution comment.

---

## License

FlagHub inherits FlagKit's MIT license:

```
Copyright (c) 2016 Bowtie AB
Copyright (c) 2026 Alpaq92
```

See [LICENSE](../LICENSE).
