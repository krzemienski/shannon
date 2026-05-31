# iOS / macOS Validation

> Real-system validation for iOS / macOS apps: boot the simulator, install the app, launch via deep link, capture screenshots + video + logs, verify UI state. No mocks. No XCTests-as-validation. The build you install is the build you validate.

## Detection signals

| Marker | Platform |
|--------|----------|
| `.xcodeproj` | iOS or macOS (project-based) |
| `.xcworkspace` | iOS or macOS (workspace, usually with CocoaPods/SPM) |
| `Package.swift` | Swift Package (often a library; check for executable target) |
| `Podfile` | CocoaPods-managed |
| `Cartfile` | Carthage-managed |
| `Project.swift` (Tuist) | Tuist-generated |

iOS vs macOS:
- iOS: target SDK contains `iphoneos`, `xrOS`, or similar
- macOS: target SDK contains `macosx`

## Required tooling

```bash
# Verify presence:
xcodebuild -version
xcrun simctl list devices booted
xcrun simctl io --help

# These should all return 0. If xcodebuild is missing, install Xcode + the
# command line tools (xcode-select --install).
```

For headless validation (no Xcode UI), `xcrun simctl` + `xcodebuild` is sufficient. The validation reference patterns in `skills/ios-validation-runner/` go deeper on the SETUP → RECORD → ACT → COLLECT → VERIFY protocol.

## Validation protocol

### Phase 0 — Pick a simulator

```bash
# List available iOS simulators
xcrun simctl list devices iOS available | head -20

# Use a deterministic device for reproducibility — don't trust "latest"
SIM_NAME="iPhone 15 Pro"
SIM_UDID=$(xcrun simctl list devices iOS available \
  | grep -i "$SIM_NAME" \
  | head -1 \
  | grep -oE '\(([0-9A-F-]{36})\)' \
  | tr -d '()')
[ -n "$SIM_UDID" ] || { echo "no simulator matching $SIM_NAME"; exit 1; }

echo "$SIM_UDID" > e2e-evidence/sim-udid.txt
```

Record the UDID in evidence — replays must use the SAME simulator.

### Phase 1 — Boot

```bash
# Boot the simulator (idempotent — no-op if already booted)
xcrun simctl bootstatus $SIM_UDID -b

# Open the Simulator.app so the UI is visible (optional but useful for screenshots)
open -a Simulator --args -CurrentDeviceUDID $SIM_UDID

# Wait for the simulator to be fully ready
while ! xcrun simctl getenv $SIM_UDID HOME >/dev/null 2>&1; do
  sleep 1
done
```

### Phase 2 — Build

```bash
SCHEME="MyApp"  # match your scheme name
BUNDLE_ID="com.example.myapp"
CONFIG="Debug"

xcodebuild \
  -project MyApp.xcodeproj \
  -scheme $SCHEME \
  -configuration $CONFIG \
  -destination "platform=iOS Simulator,id=$SIM_UDID" \
  -derivedDataPath ./build \
  build 2>&1 | tee e2e-evidence/build.log

[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "BUILD_FAIL"; exit 1; }

APP_PATH=$(find ./build -name "$SCHEME.app" -type d | head -1)
echo "app at $APP_PATH" > e2e-evidence/app-path.txt
```

For `.xcworkspace`, use `-workspace MyApp.xcworkspace -scheme MyApp`.

### Phase 3 — Install + launch

```bash
# Install the freshly-built app
xcrun simctl install $SIM_UDID "$APP_PATH"

# Start log streaming BEFORE launching, so the launch log itself is captured
xcrun simctl spawn $SIM_UDID log stream \
  --predicate "subsystem == \"$BUNDLE_ID\"" \
  --info --debug \
  > e2e-evidence/app.log 2>&1 &
LOG_PID=$!
trap 'kill $LOG_PID 2>/dev/null' EXIT

# Launch the app
xcrun simctl launch $SIM_UDID $BUNDLE_ID 2>&1 | tee e2e-evidence/launch.log

# Wait for the app's first screen to render
sleep 2
```

### Phase 4 — Record video for the whole validation

```bash
# Start screen recording. SIGINT stops cleanly; SIGKILL corrupts the file.
xcrun simctl io $SIM_UDID recordVideo \
  --codec=h264 --mask=ignored \
  e2e-evidence/run.mov &
REC_PID=$!

# At end of validation:
#   kill -SIGINT $REC_PID && wait $REC_PID
```

Use `--codec=h264` for portability. Don't use HEVC unless you know your reviewer can play it.

### Phase 5 — Per-journey capture

For every user journey (login, create item, sync, etc.):

```bash
# Capture the starting screen
xcrun simctl io $SIM_UDID screenshot e2e-evidence/journey-01-start.png

# Drive the app via deep link or UI action
xcrun simctl openurl $SIM_UDID "myapp://create-session?name=test"

sleep 1
xcrun simctl io $SIM_UDID screenshot e2e-evidence/journey-01-after-deeplink.png

# Optional: simulate a button tap via accessibility action
# (requires the app to expose accessibility identifiers)
xcrun simctl ui $SIM_UDID activate-accessibility-element \
  --bundle $BUNDLE_ID --identifier "createButton"

sleep 1
xcrun simctl io $SIM_UDID screenshot e2e-evidence/journey-01-after-tap.png
```

### Phase 6 — Status bar override (clean screenshots)

For polished screenshots, override the status bar to a clean state:

```bash
xcrun simctl status_bar $SIM_UDID override \
  --time "9:41" \
  --dataNetwork wifi --wifiMode active --wifiBars 3 \
  --cellularMode active --cellularBars 4 \
  --batteryState charged --batteryLevel 100
```

Reset before exit:

```bash
xcrun simctl status_bar $SIM_UDID clear
```

### Phase 7 — Verify per journey

For each captured screenshot:
1. Open it (`open` on macOS, or include it in the validation report)
2. Compare to the expected state per the plan
3. If the screen shows error UI, error toast, missing data, or crash dialog: FAIL
4. If accessibility tree shows missing labels (announced separately), FAIL on that

```bash
# Optional: dump the accessibility hierarchy
xcrun simctl ui $SIM_UDID describe \
  > e2e-evidence/journey-01-accessibility.txt
```

### Phase 8 — Stop recording + verdict

```bash
kill -SIGINT $REC_PID
wait $REC_PID
ls -la e2e-evidence/run.mov  # confirm it was written (non-zero bytes)

# Verdict
cat > e2e-evidence/journey-01.verdict.md <<EOF
**Journey**: create-session via deep link
**Expected**: deep link opens app, lands on create form, tap submit → success toast → list shows new session
**Observed**:
  - deep link opened app: journey-01-after-deeplink.png ✓
  - tap fired: journey-01-after-tap.png shows success toast ✓
  - list updated: list shows "test" session ✓
  - app.log shows no crashes / errors ✓
**Verdict**: PASS
**Evidence**: journey-01-{start,after-deeplink,after-tap}.png, app.log, run.mov
EOF
```

## macOS validation (different surface)

macOS apps run as host processes — there's no simulator.

```bash
xcodebuild -project MyApp.xcodeproj -scheme MyApp build
APP=./build/Build/Products/Debug/MyApp.app

# Run the app from the build output
open "$APP" --args --validation-mode=true

# Capture window screenshots via screencapture
screencapture -W e2e-evidence/macos-main-window.png

# AppleScript / accessibility to drive interactions
osascript -e 'tell application "MyApp" to activate'
```

For macOS, prefer screenshot-based evidence + log capture (`log show --predicate ...`) over deep links. The journey protocol is similar; the tooling differs.

## Iron Rule for iOS

NEVER write XCTests, snapshot tests, or any unit-test files as part of validation. The validation IS the simulator run; the evidence is screenshots, video, and log output.

NEVER mock the backend the app talks to. If your iOS app hits an API, start that real API (Docker, local instance, sandbox endpoint) and validate end-to-end through it.

NEVER skip the video recording. If a screenshot is ambiguous, the video resolves the ambiguity.

## Common anti-patterns

| Anti-pattern | Why it's wrong | Do this instead |
|--------------|----------------|------------------|
| Running XCTests as "validation" | Tests can pass while shipping bundle doesn't even build | xcodebuild the real app, install, launch, drive |
| Sleep-and-hope timing | Race conditions hide intermittent failures | Poll for readiness (boot status, app process, accessibility ready) |
| Not capturing video | Hard to debug "app got stuck" reports | Always record run.mov; use SIGINT to stop |
| Using "latest" simulator | Validation isn't reproducible | Pin the device by name + UDID |
| Skipping log stream | App crashes silently in screenshots | Always tail the app log alongside UI capture |
| HEVC video codec | Reviewers can't play it | Use h264 for portability |

## Cross-references

- `skills/ios-validation-runner/` — deeper SETUP → RECORD → ACT → COLLECT → VERIFY protocol
- `skills/visual-inspection/` — per-screenshot QA against Apple HIG checklist
- `references/api-validation.md` — validate the backend the iOS app hits
- `references/fullstack-validation.md` — full-stack composition
- `skills/no-mocking-validation-gates/` — prevents the XCTest temptation
