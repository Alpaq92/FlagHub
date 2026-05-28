//
//  SwiftUI.swift
//  FlagKit
//
//  SwiftUI bridging for FlagKit. See issue #93.
//

#if canImport(SwiftUI)

import SwiftUI

@available(iOS 13.0, tvOS 13.0, macOS 10.15, visionOS 1.0, *)
public extension Image {

    /// Wraps an existing ``Flag``'s underlying raster image in a SwiftUI ``Image``.
    ///
    /// Because FlagKit currently ships rasterised PNG assets rather than
    /// vector PDFs, SwiftUI's default scaling can produce a soft / pixelated
    /// result at non-`@1x` sizes. Apply `.interpolation(.high)` and
    /// `.resizable()` for sharper results when sizing flags above their
    /// native pixel dimensions:
    ///
    /// ```swift
    /// Image(flag: flag)?
    ///     .resizable()
    ///     .interpolation(.high)
    ///     .aspectRatio(contentMode: .fit)
    ///     .frame(width: 120)
    /// ```
    init(flag: Flag) {
        #if os(iOS) || os(tvOS) || os(visionOS)
        self = Image(uiImage: flag.originalImage)
        #elseif os(macOS)
        self = Image(nsImage: flag.originalImage)
        #endif
    }

    /// Looks up a flag by country / region code and wraps the result in a
    /// SwiftUI ``Image``. Returns `nil` if no flag asset exists for the
    /// given code.
    init?(flagWithCountryCode countryCode: String) {
        guard let flag = Flag(countryCode: countryCode) else { return nil }
        self.init(flag: flag)
    }

    #if os(iOS) || os(tvOS) || os(visionOS)
    /// Looks up a flag by country / region code and returns a styled SwiftUI
    /// ``Image`` (rounded, square, or circular). Returns `nil` if no flag
    /// asset exists for the given code.
    ///
    /// Styled rendering is only available on iOS, tvOS, and visionOS - on
    /// macOS this initializer is not present and `init(flag:)` should be
    /// used instead.
    init?(flagWithCountryCode countryCode: String, style: FlagStyle) {
        guard let flag = Flag(countryCode: countryCode) else { return nil }
        self = Image(uiImage: flag.image(style: style))
    }
    #endif
}

#endif
