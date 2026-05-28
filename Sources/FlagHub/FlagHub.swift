//
//  Copyright © 2017 Bowtie. All rights reserved.
//

import Foundation

/// Namespace for FlagHub bundle access. Declared as an `enum` (with no cases)
/// rather than a `class` so it cannot be instantiated and, more importantly,
/// does not shadow the module name of the same name.
///
/// See <https://github.com/apple/swift/issues/56573> — when a class shares
/// its name with the module it lives in, Swift's `.swiftinterface` generation
/// under `BUILD_LIBRARY_FOR_DISTRIBUTION=YES` (required for xcframeworks)
/// fails because `FlagHub.FlagStyle` gets resolved as
/// `FlagHub.FlagHub.FlagStyle` and can't find the member.
public enum FlagHub {
    public static var assetBundle: Bundle {
        #if SWIFT_PACKAGE
        return Bundle.module
        #else
        return Bundle(for: BundleLocator.self)
        #endif
    }

    /// Private marker class used solely to anchor `Bundle(for:)` lookups in
    /// the non-SPM (Xcode framework / CocoaPods / Carthage) build path. The
    /// inner class avoids the module-name shadow that the outer namespace
    /// would otherwise introduce.
    private final class BundleLocator {}
}
