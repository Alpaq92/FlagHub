![FlagHub 3.0](header.png)

# FlagHub

<div align="center">

[![Build](https://img.shields.io/github/actions/workflow/status/Alpaq92/FlagHub/ci.yml?branch=main&label=build)](https://github.com/Alpaq92/FlagHub/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/Alpaq92/FlagHub?label=release&sort=semver)](https://github.com/Alpaq92/FlagHub/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Alpaq92/FlagHub/total?label=downloads&color=blue&cacheSeconds=300)](https://github.com/Alpaq92/FlagHub/releases)
[![Last commit](https://img.shields.io/github/last-commit/Alpaq92/FlagHub)](https://github.com/Alpaq92/FlagHub/commits/main)
[![Commit activity](https://img.shields.io/github/commit-activity/m/Alpaq92/FlagHub?label=commits%2Fmonth)](https://github.com/Alpaq92/FlagHub/commits/main)<br>
[![Open PRs](https://img.shields.io/github/issues-pr/Alpaq92/FlagHub?label=openned%20PRs)](https://github.com/Alpaq92/FlagHub/pulls)
[![SwiftPM compatible](https://img.shields.io/badge/SPM-compatible-brightgreen)](https://swift.org/package-manager)
[![Carthage compatible](https://img.shields.io/badge/Carthage-compatible-brightgreen)](https://github.com/Carthage/Carthage)
[![Platforms](https://img.shields.io/badge/platforms-iOS%20%7C%20macOS%20%7C%20tvOS%20%7C%20visionOS-lightgrey)](Package.swift)
[![License](https://img.shields.io/github/license/Alpaq92/FlagHub?color=blue)](LICENSE)

</div>

Apple-platforms flag-icon library. Fork of [madebybowtie/FlagKit](https://github.com/madebybowtie/FlagKit) — every open upstream PR merged, packaging issues fixed, two Swift API conveniences added. The flag artwork is identical to upstream.

**256 flags. iOS · macOS · tvOS · visionOS.**

For a detailed overview of this project's state, see [docs/OVERVIEW.md](docs/OVERVIEW.md).

## Install

Swift Package Manager:

```swift
.package(url: "https://github.com/Alpaq92/FlagHub.git", branch: "main")
```

Or CocoaPods / Carthage / drop `Sources/FlagHub/FlagHub.xcassets` into your target.

## Use

```swift
import FlagHub

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

- [**docs/OVERVIEW.md**](docs/OVERVIEW.md) — deep dive: merged PRs and resolved issues per tier, what was deliberately not done, PNG optimization detail, install matrix, full Swift / SwiftUI usage, project layout, helper scripts, automation, maintenance
- [CHANGELOG.md](CHANGELOG.md) — Keep-a-Changelog log; `[Unreleased]` is auto-populated by the changelog workflow
- [.github/AUTOMATION.md](.github/AUTOMATION.md) — CI / CodeQL / auto-merge / release pipeline

## How it was built

This fork was developed with **audit-based AI assistance** — an AI agent proposed each change, but every edit was reviewed against the upstream codebase, the project's intent, and visible inline previews before being committed. The audit trail is in the commit log: the `Polish` / `Revert` commits show where AI-generated content was reviewed, deemed below quality, and rolled back to upstream artwork. No artwork in this branch is AI-generated; the code additions (`Flag.all`, `Image(flag:)`) are reviewed line-by-line in `Sources/FlagHub/FlagCodes.swift` and `Sources/FlagHub/SwiftUI.swift`.

## License

MIT — see [LICENSE](LICENSE). Original copyright Bowtie AB (2016); fork copyright Alpaq92 (2026).
