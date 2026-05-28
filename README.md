![Header](header.png)

<div align="center">
<a href="https://github.com/Carthage/Carthage" target="_blank">
<img src="https://img.shields.io/badge/Carthage-Compatible-brightgreen.svg?style=flat" />
</a>

<a href="https://cocoapods.org/pods/FlagKit" target="_blank">
<img src="https://img.shields.io/cocoapods/v/FlagKit.svg?style=flat" />
</a>
</div>

# FlagHub — FlagKit, kept alive

> **This is a fork of [madebybowtie/FlagKit](https://github.com/madebybowtie/FlagKit).** The upstream repo has been dormant since 2020. This fork merges every open upstream PR, fixes a small set of infrastructure / cleanup issues, and adds two Swift API conveniences. The flag artwork itself is pristine upstream — no hand-drawn replacements ship here. See [FORK.md](FORK.md) for the full change log including what was deliberately *not* done and why.

Beautiful flag icons for usage in apps and on the web. All flags are provided as stand-alone PNG and SVG files. FlagHub also provides an Asset Catalog and framework for easy use on Apple platforms.

The bundled asset set carries **256 flags** — the same set as upstream FlagKit.

## What's different from upstream

**Merged pull requests** (all seven open ones):

- [#65](https://github.com/madebybowtie/FlagKit/pull/65) `Flag.emoji` accessor
- [#79](https://github.com/madebybowtie/FlagKit/pull/79) updated podspec
- [#82](https://github.com/madebybowtie/FlagKit/pull/82) ZA flag sizing fix
- [#100](https://github.com/madebybowtie/FlagKit/pull/100) `resource` → `resource_bundle` migration
- [#107](https://github.com/madebybowtie/FlagKit/pull/107) visionOS support
- [#109](https://github.com/madebybowtie/FlagKit/pull/109) updated SY flag (free Syria green)
- [#110](https://github.com/madebybowtie/FlagKit/pull/110) updated IR flag (Lion and Sun)

**Resolved issues:**

- [#66](https://github.com/madebybowtie/FlagKit/issues/66) SVG element IDs are scoped per file so multiple flags inlined into the same DOM no longer cross-reference each other's gradients
- [#91](https://github.com/madebybowtie/FlagKit/issues/91) CH and VA are now square (15×15)
- [#92](https://github.com/madebybowtie/FlagKit/issues/92) `Flag.all` / `Flag.supportedCountryCodes`
- [#93](https://github.com/madebybowtie/FlagKit/issues/93) SwiftUI `Image(flag:)` initialisers
- [#95](https://github.com/madebybowtie/FlagKit/issues/95) WW (world / default) flag restored
- [#98](https://github.com/madebybowtie/FlagKit/issues/98) broken README sample-project link removed
- [#106](https://github.com/madebybowtie/FlagKit/issues/106) every SVG carries an MIT attribution header

**Other quality-of-life work:**

- Every PNG in the repo recompressed losslessly with `oxipng` — 41.7% smaller (2.3 MiB → 1.4 MiB) with zero quality loss
- Title banner refreshed (`header.png`)

## Installation (iOS, macOS, tvOS, visionOS)

FlagHub is consumed exactly like upstream FlagKit. Point your package manager at this fork's URL.

### SwiftPM

```
https://github.com/<your-username>/FlagHub.git
```

(or the upstream URL `https://github.com/madebybowtie/FlagKit.git` if you only need the PR-merged subset).

### Carthage

```
github "madebybowtie/FlagKit"
```

### CocoaPods

```
pod 'FlagKit'
```

### Manual

Add `Sources/FlagKit/FlagKit.xcassets` to your target.

## Usage

FlagKit provides both rectangular unstyled flags and styled flags in a variety of shapes — rounded corners, square, and circle.

> **Note:** Styling is currently not supported on macOS.

### Basic lookup

```swift
let countryCode = Locale.current.regionCode!
let flag = Flag(countryCode: countryCode)!

let originalImage = flag.originalImage              // unstyled
let styledImage   = flag.image(style: .circle)      // iOS / tvOS / visionOS
```

### Emoji

```swift
Flag(countryCode: "JP")?.emoji  // "🇯🇵"
```

### Enumerating every flag

```swift
// 256 codes — ISO 3166-1 alpha-2 plus EU, WW, LGBT, GB-ENG/NIR/SCT/WLS/ZET, US-CA.
Flag.supportedCountryCodes      // ["AD", "AE", "AF", …]

// Materialised flags in the same order.
Flag.all                        // [Flag, Flag, Flag, …]
```

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

Apply `.interpolation(.high)` and `.resizable()` when rendering above the asset's native pixel size to avoid soft / pixelated output.

### Direct bundle access

```swift
let bundle = FlagKit.assetBundle
let originalImage = UIImage(named: countryCode, in: bundle, compatibleWith: nil)
```

## Reference

A full table of every supported flag is in [Assets/Flags.md](Assets/Flags.md). Repo conventions and build helpers — `scripts/scope_svg_ids.py`, `scripts/add_svg_attribution.py`, `scripts/optimize_pngs.py` — are documented in [FORK.md](FORK.md).

## Contributing

The flag artwork in this fork is intentionally kept identical to upstream's. If you want to add or replace a flag, please open an upstream PR against [madebybowtie/FlagKit](https://github.com/madebybowtie/FlagKit) — that's where the design canon lives. Infrastructure improvements (build / packaging / Swift API) are welcome here directly.

## License

FlagHub inherits FlagKit's MIT license. See [LICENSE](LICENSE).
