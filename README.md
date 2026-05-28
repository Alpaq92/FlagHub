![Header](header.png)

# FlagHub

Apple-platforms flag-icon library. Fork of [madebybowtie/FlagKit](https://github.com/madebybowtie/FlagKit) — every open upstream PR merged, packaging issues fixed, two Swift API conveniences added. The flag artwork is identical to upstream.

**256 flags. iOS · macOS · tvOS · visionOS.**

For a detailed overview of this project's state, see [docs/OVERVIEW.md](docs/OVERVIEW.md).

## Install

Swift Package Manager:

```swift
.package(url: "https://github.com/<owner>/FlagHub.git", branch: "main")
```

Or CocoaPods / Carthage / drop `Sources/FlagKit/FlagKit.xcassets` into your target.

## Use

```swift
import FlagKit

let flag = Flag(countryCode: "JP")!
flag.originalImage          // UIImage / NSImage
flag.image(style: .circle)  // styled, iOS / tvOS / visionOS only
flag.emoji                  // "🇯🇵"

Flag.all                    // every flag, ordered alphabetically
```

SwiftUI:

```swift
Image(flagWithCountryCode: "PL")?
    .resizable()
    .interpolation(.high)
    .frame(width: 32)
```

## Docs

- [**docs/OVERVIEW.md**](docs/OVERVIEW.md) — deep dive: install details, full Swift / SwiftUI usage, project layout, helper scripts, automation, maintenance
- [FORK.md](FORK.md) — every commit grouped by upstream PR / issue, plus what was attempted and reverted
- [.github/README.md](.github/README.md) — CI / CodeQL / auto-merge / release pipeline

## License

MIT — see [LICENSE](LICENSE).
