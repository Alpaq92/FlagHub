# Fork notes

This branch (`fork-flagkit`) is a fork of [madebybowtie/FlagKit](https://github.com/madebybowtie/FlagKit) created to clear out the stalled-PR and open-issue backlog. The upstream repository has not seen a release since 2.3 (2020); pull requests have been queued since 2018 and a number of factual / accuracy bugs in individual flags have gone unaddressed.

Everything below was applied on top of upstream `master`.

---

## Upstream PRs merged

All seven open pull requests on upstream were fast-forwarded onto this fork. Conflicts were resolved in favour of the fork's working state (see commit messages for the call on each):

| Upstream PR | Title | Notes |
|---|---|---|
| [#65](https://github.com/madebybowtie/FlagKit/pull/65) | Add `Flag.emoji` accessor | Clean merge |
| [#79](https://github.com/madebybowtie/FlagKit/pull/79) | Update `FlagKit.podspec` | Conflict in `swift_versions` — kept the newer list (5.0–5.3) from master; PR was stale |
| [#82](https://github.com/madebybowtie/FlagKit/pull/82) | Fix sizing of ZA flags | Clean merge |
| [#100](https://github.com/madebybowtie/FlagKit/pull/100) | Migrate `resource` → `resource_bundle` | Clean merge |
| [#107](https://github.com/madebybowtie/FlagKit/pull/107) | Add visionOS support | Conflict in `Flag.swift` — kept #65's emoji block alongside #107's `os(visionOS)` guard |
| [#109](https://github.com/madebybowtie/FlagKit/pull/109) | Update SY flag (free Syria green) | Clean merge |
| [#110](https://github.com/madebybowtie/FlagKit/pull/110) | Update IR flag (Lion and Sun) | Conflict on `IR.imageset/IR.png` — dropped, consistent with PR #100's removal of 1x PNGs from xcassets; kept the new @2x/@3x |

---

## Upstream issues resolved

### Tier 1 — bug fixes and infrastructure
| Issue | Title | Resolution |
|---|---|---|
| [#66](https://github.com/madebybowtie/FlagKit/issues/66) | SVG gradient IDs collide across files | Scoped 2,645 element IDs and rewrote 1,462 references across all 255 SVGs; helper at `scripts/scope_svg_ids.py` is idempotent |
| [#91](https://github.com/madebybowtie/FlagKit/issues/91) | CH and VA should be square | Both SVGs re-aspected to 15×15 via centred `viewBox` crop |
| [#95](https://github.com/madebybowtie/FlagKit/issues/95) | WW (default world) flag removed in 2.0 | Restored from the parent of `a7b7d9e` into `Assets/PNG/` and the xcassets imageset |
| [#98](https://github.com/madebybowtie/FlagKit/issues/98) | Broken README sample-project link | Removed (the target path never existed in any history) |
| [#106](https://github.com/madebybowtie/FlagKit/issues/106) | Add MIT attribution comments to each SVG | Prepended to all 255 SVGs; helper at `scripts/add_svg_attribution.py` is idempotent |

### Tier 2 — single-flag visual corrections
| Issue | Title | Resolution |
|---|---|---|
| [#62](https://github.com/madebybowtie/FlagKit/issues/62) | CN flag is wrong | Regenerated all 5 stars from the official 1949 construction sheet, with each small star rotated toward the big star centre (helper at `scripts/compute_cn_stars.py`) |
| [#70](https://github.com/madebybowtie/FlagKit/issues/70) | MD flag is wrong | Replaced the brown M-shape placeholder with a layered coat of arms — golden eagle with spread wings holding a scepter and olive branch in its talons, eagle head with Orthodox cross above, heraldic escutcheon split red/blue, golden aurochs head inside with horns, eyes, snout, 8-point star, silver crescent, and golden rose |
| [#76](https://github.com/madebybowtie/FlagKit/issues/76) | US flag has 15 stripes | Rewrote stripe path with `15/13` band height (7 red), resized canton to `15·7/13` tall, and replaced the 18 circle approximations in the canton with 50 spec-correct five-point stars in a 6/5/6/5/6/5/6/5/6 layout |
| [#96](https://github.com/madebybowtie/FlagKit/issues/96) | ZW flag is wrong | Added the missing Zimbabwe Bird (Hungwe) silhouette — body, hooked beak, tail-feather fan, two legs, banded soapstone plinth — centered over the red star |
| [#104](https://github.com/madebybowtie/FlagKit/issues/104) | AL flag has wrong shape and red | Red shifted from `#EE343C..#E2222A` to `#D81E2A..#BE0E22` (closer to Pantone 186); abstract X-shape replaced with a stylised double-headed eagle (hourglass body, primary-feather scallops on each wing, hooked beaks, eye dots, 7-feather tail, talons) |

### Tier 3 — missing flags
Issues [#36](https://github.com/madebybowtie/FlagKit/issues/36), [#73](https://github.com/madebybowtie/FlagKit/issues/73), [#83](https://github.com/madebybowtie/FlagKit/issues/83), [#84](https://github.com/madebybowtie/FlagKit/issues/84), [#97](https://github.com/madebybowtie/FlagKit/issues/97), [#101](https://github.com/madebybowtie/FlagKit/issues/101) collectively requested a long list of additional flag codes. Nine were added:

| Code | Subject |
|---|---|
| AC | Ascension Island |
| AQ | Antarctica |
| BQ | Bonaire, Sint Eustatius & Saba |
| CP | Clipperton Island |
| DG | Diego Garcia (BIOT) |
| EA | Ceuta & Melilla |
| EH | Western Sahara |
| IC | Canary Islands |
| TA | Tristan da Cunha |

`Assets/Flags.md` was updated to list them (count 256 → 265). PNG generation for these is **deferred** — see "What was not done" below.

### Tier 4 — code features
| Issue | Title | Resolution |
|---|---|---|
| [#81](https://github.com/madebybowtie/FlagKit/issues/81) | Swift Package Manager support | **Already done upstream** — `Package.swift` exists at repo root, kept as-is |
| [#92](https://github.com/madebybowtie/FlagKit/issues/92) | "Get all flags in one call" | Added `Flag.supportedCountryCodes: [String]` and `Flag.all: [Flag]` in `Sources/FlagKit/FlagCodes.swift` |
| [#93](https://github.com/madebybowtie/FlagKit/issues/93) | Pixelated images in SwiftUI | Added `Image(flag:)`, `Image(flagWithCountryCode:)`, and `Image(flagWithCountryCode:style:)` in `Sources/FlagKit/SwiftUI.swift`. The pixelation root cause (raster-only PNG assets) is not fully solved — see deferred work — but the bundled docs now point consumers at `.interpolation(.high)` and `.resizable()` for sharper SwiftUI rendering |

---

## What was not done, and why

### PNG regeneration for visually-modified flags
**Affected:** CH, VA (Tier 1 square fix); AL, CN, MD, US, ZW (Tier 2 visual fixes); AC, AQ, BQ, CP, DG, EA, EH, IC, TA (Tier 3 new flags).

The repository ships rasterised `@1x`, `@2x`, `@3x` PNGs alongside the SVGs in `Assets/PNG/` and inside `Sources/FlagKit/FlagKit.xcassets/<CODE>.imageset/`. No SVG→PNG rasterizer was available in the environment this fork was built in (`ImageMagick`, `Inkscape`, `rsvg-convert`, and `cairosvg` are all missing). The SVG fixes therefore are not reflected in the PNG assets that the Asset Catalog (and consequently `Flag.originalImage`) actually loads.

To finish this work locally, regenerate every changed/new flag's PNGs from its SVG at 1×, 2×, and 3× of the canonical 21×15 size (so 21×15, 42×30, 63×45 respectively — or 15×15 / 30×30 / 45×45 for the square CH and VA). Tooling like `rsvg-convert` or batch-scripted Inkscape works fine for this.

### xcassets registration for the nine new Tier 3 flags
Same root cause — the imageset folders weren't created because there are no PNGs to put in them yet. Once PNGs exist, each new code needs:
1. A new `Sources/FlagKit/FlagKit.xcassets/<CODE>.imageset/` directory.
2. A `Contents.json` matching the post-#100 pattern (no `1x` filename — only `@2x` and `@3x`).
3. The corresponding `@2x.png` and `@3x.png` files.

Until then `Flag(countryCode:)` returns `nil` for these nine codes and `Flag.all` skips them. The SVGs are present in `Assets/SVG/` and are listed in `Flags.md`.

### Heraldic-accuracy redraws of the complex emblems
**Affected:** AL eagle, MD coat of arms, ZW bird, AC/DG/TA shields, IC coat of arms.

The reworked SVGs are hand-written silhouettes built from primitives and bezier curves. They read as the right idea at typical UI sizes (sidebar, picker, list cell) but they are not heraldically accurate at large render sizes. Producing renderings of the same quality as the rest of FlagKit's polished asset set requires a vector illustrator (Sketch / Illustrator / Affinity / Inkscape) and ideally a public-domain reference SVG to import — out of scope for raw-XML editing.

### Remaining upstream issues left untouched
| Issue | Title | Why not |
|---|---|---|
| [#89](https://github.com/madebybowtie/FlagKit/issues/89) | Port to Android | Different codebase entirely; out of scope for a Swift Package |
| [#94](https://github.com/madebybowtie/FlagKit/issues/94) | Expose SVGs to consumers | Requires bundling `Assets/SVG/` into the `resource_bundle` and adding a `Flag.svgData`/`Flag.svgURL` accessor. Mechanical follow-up — not done in this round |
| [#99](https://github.com/madebybowtie/FlagKit/issues/99) | Placeholder "unknown" flags | The restored WW flag (#95) partly addresses this; further "unknown" variants (pirate, question-mark, etc.) are a design judgement call |
| [#102](https://github.com/madebybowtie/FlagKit/issues/102) | Slow compile times | Needs profiling to find the root cause (likely xcassets size). No measurement was taken |
| [#103](https://github.com/madebybowtie/FlagKit/issues/103) | AZ flag not working | No reproduction provided in the issue; cannot diagnose without more info from the reporter |
| [#105](https://github.com/madebybowtie/FlagKit/issues/105) | Flags not displaying in web | FlagKit is an Apple-platforms library; the issue lacks any reproduction or codebase reference |
| [#111](https://github.com/madebybowtie/FlagKit/issues/111) | "Abandoned?" | Meta question; this fork itself is the answer |

---

## PNG optimization

Every raster asset in the repo has been recompressed losslessly. The upstream PNGs were exported from Sketch's `sketchtool` and were not run through any post-export optimiser, so they carried ~40% recoverable overhead.

### Tool comparison

| Tool | Type | Typical reduction here | Notes |
|---|---|---|---|
| `pngcrush` | lossless | ~10–20% | Older, slow, low yield |
| `OptiPNG` | lossless | ~20–30% | Reference C implementation; single-threaded |
| **`oxipng`** | **lossless** | **~42%** | Pure-Rust port of OptiPNG, multithreaded, deflate strategy is more exhaustive at the same level |
| `pngquant` | lossy (palette) | 50–70% | Rejected for this asset set — the subtle top-to-bottom linear gradients defined in every flag SVG (see `linearGradient` defs) would be at risk of visible posterisation or banding once quantised to a 256-colour palette |

`oxipng` was chosen as the best fit: it produces lossless output, so it cannot degrade the gradient fidelity that distinguishes FlagKit's flags from generic flag sets, and its yield is materially higher than the older lossless tools.

### Results

| Path | Files | Before | After | Saved |
|---|---:|---:|---:|---:|
| `Assets/PNG/` | 768 | 1,374 KiB | 798 KiB | 42% |
| `Sources/FlagKit/FlagKit.xcassets/` | 512 | 882 KiB | 504 KiB | 43% |
| `Header.png` | 1 | 100 KiB | 71 KiB | 29% |
| **Total** | **1,281** | **2,356 KiB** | **1,373 KiB** | **41.7%** |

To re-run after editing PNG assets:

```sh
pip install pyoxipng
python scripts/optimize_pngs.py
```

The script is idempotent — running it on an already-optimised tree either does nothing or claws back a few more bytes.

---

## Helper scripts

Python utilities in `scripts/`, all idempotent — running them on a clean tree is a no-op:

| Script | Purpose |
|---|---|
| `scripts/scope_svg_ids.py` | Prefixes every SVG's local element IDs with the country code to prevent cross-document `url(#…)` collisions (#66) |
| `scripts/add_svg_attribution.py` | Prepends a standard MIT attribution comment to every SVG (#106) |
| `scripts/compute_cn_stars.py` | Reproduces the spec-correct star polygon coordinates for the CN flag (#62) — invoked once to populate `CN.svg`; kept in-tree as a documentation of the construction-sheet math |
| `scripts/compute_us_stars.py` | Reproduces the 50-star canton layout for the US flag (#76) — same role as the CN script |
| `scripts/optimize_pngs.py` | Losslessly recompresses every PNG in the repo with `oxipng -o 6`. See [PNG optimization](#png-optimization) above for the tool-choice rationale |
