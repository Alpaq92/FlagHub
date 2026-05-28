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
                .process("FlagHub.xcassets")
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
                .process("Fixtures.xcassets")
            ]
        )
    ]
)
