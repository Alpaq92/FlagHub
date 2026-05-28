//
//  Copyright © 2017 Bowtie. All rights reserved.
//

import Foundation

/// Accessor for the bundle that ships FlagHub's flag images.
///
/// Named `FlagHubBundle` rather than `FlagHub` because a type whose name
/// matches its module name triggers Swift's `.swiftinterface` generation
/// bug under `BUILD_LIBRARY_FOR_DISTRIBUTION=YES` (required for xcframework
/// distribution). The compiler emits `'FlagHub.FlagHub' shadows module
/// 'FlagHub'` and then fails to resolve `FlagStyle` and `Flag` from the
/// generated interface because lookups bind to the type before the module.
///
/// See <https://github.com/apple/swift/issues/56573>.
public enum FlagHubBundle {
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
