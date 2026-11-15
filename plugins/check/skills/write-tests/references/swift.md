# Swift testing notes (iOS and macOS)

## Running tests
- One test in Xcode: `xcodebuild test -scheme App -destination 'platform=iOS Simulator,name=iPhone 16' -only-testing:AppTests/TitleLimitTests/testAcceptsAtMost80Characters`
- One suite with SwiftPM: `swift test --filter TitleLimitTests`

## Tools
- **Framework:** XCTest. Newer toolchains also offer Swift Testing (`@Test`, `#expect`).
- **Clock:** inject a `Clock`, or a `now: () -> Date` closure. Logic never calls `Date()` directly.
- **Network fakes:** a `URLProtocol` subclass that replays recorded responses, or a transport behind a protocol.
- **Storage:** real SQLite or Core Data, in a temporary directory made for each test.
- **UI:** XCUITest for flows, snapshot tests for key screens.
- **Lint:** SwiftLint in CI.

## Habits
- Outside tests, never use `try!` or force unwraps. Inside tests, prefer `XCTUnwrap`.
- Verify background behaviour (location, background tasks) on a real device. The simulator catches logic errors only.

## Sample
```swift
final class TitleLimitTests: XCTestCase {
    func testAcceptsAtMost80Characters() {
        XCTAssertTrue(Note.titleFits(String(repeating: "a", count: 80)))
        XCTAssertFalse(Note.titleFits(String(repeating: "a", count: 81)))
    }
}
```
