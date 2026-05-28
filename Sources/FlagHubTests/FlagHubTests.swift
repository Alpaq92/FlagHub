//
//  Copyright © 2017 Bowtie. All rights reserved.
//

import XCTest
import FlagHub

class FlagHubTests: XCTestCase {
    func testAssetBunde() {
        let bundle = FlagHub.assetBundle
        XCTAssertNotNil(bundle)
    }
}
