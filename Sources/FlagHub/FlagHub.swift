//
//  Copyright © 2017 Bowtie. All rights reserved.
//

import Foundation

public class FlagHub {
    public static var assetBundle: Bundle {
        get {
            #if SWIFT_PACKAGE
            return Bundle.module
            #else
            return Bundle(for: FlagHub.self)
            #endif
        }
    }
}
