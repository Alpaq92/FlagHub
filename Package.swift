// swift-tools-version:5.3
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "FlagHub",
    platforms: [
        .iOS(.v12),
        .tvOS(.v12),
        .macOS(.v10_13)
    ],
    products: [
        .library(name: "FlagHub", targets: ["FlagHub"]),
    ],
    dependencies: [],
    targets: [
        .target(
            name: "FlagHub",
            dependencies: [],
            exclude: [
                "Info.plist",
                "FlagHubFramework.xcconfig"
            ],
            resources: [
                // .copy (not .process) preserves the xcassets folder structure
                // inside the bundle so the macOS NSImage path can read PNGs
                // directly by URL. Xcode-built frameworks still compile the
                // catalog the normal way.
                .copy("FlagHub.xcassets")
            ]
        ),
        .testTarget(
            name: "FlagHubTests",
            dependencies: ["FlagHub"],
            exclude: [
                "Info.plist",
                "FlagHubTests.xcconfig",
                "ObjectiveCTests.m"
            ],
            resources: [
                .copy("Fixtures.xcassets")
            ]
        )
    ]
)
