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

### Tier 2 — single-flag visual corrections (not done)
Issues [#62](https://github.com/madebybowtie/FlagKit/issues/62) (CN stars), [#70](https://github.com/madebybowtie/FlagKit/issues/70) (MD coat of arms), [#76](https://github.com/madebybowtie/FlagKit/issues/76) (US 15 stripes / 18 dots), [#96](https://github.com/madebybowtie/FlagKit/issues/96) (ZW missing Hungwe bird), and [#104](https://github.com/madebybowtie/FlagKit/issues/104) (AL eagle and red) all flag genuine defects in the upstream artwork. Hand-drawn corrections for each were prototyped on this branch but **reverted** for the same reason as Tier 3: the replacement artwork did not meet the quality bar of the rest of FlagKit's asset set. The pure-geometry pieces (US stripe count, CN star positions per the 1949 construction sheet) were correct as math but still hand-edited SVGs, which is hard to justify next to professional vector artwork. Fixing these flags properly requires a vector illustrator. The commits remain in the branch history.

### Tier 3 — missing flags (not done)
Issues [#36](https://github.com/madebybowtie/FlagKit/issues/36), [#73](https://github.com/madebybowtie/FlagKit/issues/73), [#83](https://github.com/madebybowtie/FlagKit/issues/83), [#84](https://github.com/madebybowtie/FlagKit/issues/84), [#97](https://github.com/madebybowtie/FlagKit/issues/97), [#101](https://github.com/madebybowtie/FlagKit/issues/101) collectively requested a long list of additional flag codes (AC, AQ, BQ, CP, DG, EA, EH, IC, TA were the most-cited). Hand-drawn approximations of all nine were prototyped on this branch but **reverted** — the silhouettes did not meet the quality bar of upstream FlagKit's existing assets, and shipping low-fidelity flag artwork was a worse outcome than leaving the codes unsupported. The commits remain in the branch history if anyone wants to pick them up and finish them with proper vector tooling. Net: this fork carries the same 256 flags as upstream.

### Tier 4 — code features
| Issue | Title | Resolution |
|---|---|---|
| [#81](https://github.com/madebybowtie/FlagKit/issues/81) | Swift Package Manager support | **Already done upstream** — `Package.swift` exists at repo root, kept as-is |
| [#92](https://github.com/madebybowtie/FlagKit/issues/92) | "Get all flags in one call" | Added `Flag.supportedCountryCodes: [String]` and `Flag.all: [Flag]` in `Sources/FlagKit/FlagCodes.swift` |
| [#93](https://github.com/madebybowtie/FlagKit/issues/93) | Pixelated images in SwiftUI | Added `Image(flag:)`, `Image(flagWithCountryCode:)`, and `Image(flagWithCountryCode:style:)` in `Sources/FlagKit/SwiftUI.swift`. The pixelation root cause (raster-only PNG assets) is not fully solved — see deferred work — but the bundled docs now point consumers at `.interpolation(.high)` and `.resizable()` for sharper SwiftUI rendering |

---

## What was not done, and why

### PNG regeneration for the squared CH and VA SVGs
The Tier 1 viewBox crop on `CH.svg` and `VA.svg` was applied to the SVGs but the corresponding `Assets/PNG/CH*.png` and `VA*.png` (and the in-bundle xcassets PNGs) still encode the old 21×15 aspect ratio. No SVG→PNG rasterizer was available in this environment (`ImageMagick`, `Inkscape`, `rsvg-convert`, `cairosvg` are all missing). To finish locally, regenerate the six affected PNGs from the updated SVGs at 15×15, 30×30, and 45×45.

This is the only outstanding PNG regen — Tier 2 SVG changes that would have needed re-rasterising were reverted in a later commit.

### Nine missing-flag ISO codes (Tier 3)
Hand-drawn approximations for AC, AQ, BQ, CP, DG, EA, EH, IC, TA were attempted on this branch and reverted — see Tier 3 above. Adding these properly requires a vector illustrator (Sketch / Illustrator / Affinity / Inkscape) and ideally public-domain reference SVGs, which is out of scope for raw-XML editing.

### Heraldic-accuracy redraws of the complex emblems
**Affected:** the same set covered in the Tier 2 revert above (AL eagle, MD coat of arms, ZW bird, CN star geometry, US stripes-and-stars).

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
| `header.png` | 1 | 100 KiB | 71 KiB | 29% |
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
| `scripts/optimize_pngs.py` | Losslessly recompresses every PNG in the repo with `oxipng -o 6`. See [PNG optimization](#png-optimization) above for the tool-choice rationale |
