Pod::Spec.new do |s|
  s.name = "FlagHub"
  s.version = "3.0.3"
  s.summary = "Beautiful flag icons for usage in apps and on the web."
  s.swift_versions = ['5.0', '5.1', '5.2', '5.3']

  s.homepage = "https://github.com/Alpaq92/FlagHub"
  s.license = { :type => "MIT", :file => "LICENSE" }

  s.author = { "Alpaq92" => "noreply@github.com" }

  s.ios.deployment_target = "12.0"
  s.osx.deployment_target = "10.13"
  s.tvos.deployment_target = "12.0"

  s.source = { :git => "https://github.com/Alpaq92/FlagHub.git", :tag => "v#{s.version}" }
  s.source_files = "Sources/FlagHub/*.swift"
  s.resources = "Sources/FlagHub/FlagHub.xcassets"
end
