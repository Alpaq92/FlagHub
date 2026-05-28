![Header](Header.png)

<div align="center">
<a href="https://github.com/Carthage/Carthage" target="_blank">
<img src="https://img.shields.io/badge/Carthage-Compatible-brightgreen.svg?style=flat" />
</a>

<a href="https://cocoapods.org/pods/FlagKit" target="_blank">
<img src="https://img.shields.io/cocoapods/v/FlagKit.svg?style=flat" />
</a>
</div>

# FlagKit

> **This is a fork of [madebybowtie/FlagKit](https://github.com/madebybowtie/FlagKit).** The upstream repo has been dormant since 2020 with stale pull requests and a backlog of open issues. This fork merges every open upstream PR and addresses most of the open issues. See [FORK.md](FORK.md) for the full change log, including what was deliberately *not* done and why.

Beautiful flag icons for usage in apps and on the web. All flags are provided as stand-alone PNG and SVG files. FlagKit also provides an Asset Catalog and framework for easy use on Apple platforms.

The bundled asset set now contains **265 flags** including the nine ISO codes most commonly missing from competing libraries (AC, AQ, BQ, CP, DG, EA, EH, IC, TA).

## Installation (iOS, macOS, tvOS, visionOS)

FlagKit provides a framework for easy installation as a dependency. You can also manually copy the Asset Catalog into your project.

### SwiftPM
Add the following as repository URL:

```
https://github.com/madebybowtie/FlagKit.git
```

### Carthage
Add the following line to your `Cartfile`:

```
github "madebybowtie/FlagKit"
```

### CocoaPods
Add the following line to your `Podfile`:

```
pod 'FlagKit'
```

### Manual
Add `Sources/FlagKit/FlagKit.xcassets` to your target.

## Usage

FlagKit provides both rectangular unstyled flags and styled flags in a variety of shapes — rounded corners, square, and circle.

> **Note:** Styling is currently not supported by FlagKit on macOS.

### Basic lookup

```swift
let countryCode = Locale.current.regionCode!
let flag = Flag(countryCode: countryCode)!

// Retrieve the unstyled image for customized use
let originalImage = flag.originalImage

// Or retrieve a styled flag (iOS / tvOS / visionOS only)
let styledImage = flag.image(style: .circle)
```

### Emoji

```swift
Flag(countryCode: "JP")?.emoji  // "🇯🇵"
```

### Enumerating every flag

```swift
// Every code FlagKit ships an asset for (ISO 3166-1 alpha-2 plus a
// handful of additional identifiers: EU, WW, LGBT, GB-ENG/NIR/SCT/WLS/ZET,
// US-CA).
Flag.supportedCountryCodes  // ["AC", "AD", "AE", ...]

// Materialised flags, in the same alphabetical order.
Flag.all                    // [Flag, Flag, Flag, ...]
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

Use `.interpolation(.high)` and `.resizable()` when rendering above the asset's native pixel size to avoid soft / pixelated output — see [#93](https://github.com/madebybowtie/FlagKit/issues/93).

### Direct bundle access

```swift
let bundle = FlagKit.assetBundle
let originalImage = UIImage(named: countryCode, in: bundle, compatibleWith: nil)
```

## Reference

A list of all flags can be [found here](Assets/Flags.md).

## More Info

Have a question? Please [open an issue](https://github.com/madebybowtie/FlagKit/issues/new) on upstream — or read [FORK.md](FORK.md) if you're trying to figure out what this fork changed.

## License

FlagKit is released under the MIT license. See
[LICENSE](LICENSE).
