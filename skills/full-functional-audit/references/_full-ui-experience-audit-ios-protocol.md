# iOS Protocol

> `xcrun simctl` + `ios-validation-runner` patterns for Phase 2/3/6 of full-ui-experience-audit on iOS or cross-platform mobile projects.

## Setup

```bash
# Pick + boot the simulator
SIM_UDID="<from run-config.md>"
xcrun simctl bootstatus "$SIM_UDID" -b

# Open the Simulator app so screenshots / video reflect the live state
open -a Simulator --args -CurrentDeviceUDID "$SIM_UDID"

# Build the app
xcodebuild \
  -project "$APP".xcodeproj \
  -scheme "$SCHEME" \
  -configuration Debug \
  -destination "platform=iOS Simulator,id=$SIM_UDID" \
  -derivedDataPath ./build \
  build 2>&1 | tee audit-evidence/build.log

APP_PATH=$(find ./build -name "$SCHEME.app" -type d | head -1)

# Install fresh build
xcrun simctl install "$SIM_UDID" "$APP_PATH"

# Status-bar override for clean screenshots
xcrun simctl status_bar "$SIM_UDID" override \
  --time "9:41" \
  --dataNetwork wifi --wifiMode active --wifiBars 3 \
  --batteryState charged --batteryLevel 100
```

## Log stream (start before launch)

```bash
# Start streaming the app's log to disk BEFORE launching, so the launch
# log is captured
xcrun simctl spawn "$SIM_UDID" log stream \
  --predicate "subsystem == \"$BUNDLE_ID\"" \
  --info --debug \
  > audit-evidence/app.log 2>&1 &
LOG_PID=$!
trap 'kill $LOG_PID 2>/dev/null' EXIT
```

Without this, app crashes during launch are invisible — only the screen
state is captured, not the diagnostics that explain it.

## Video recording (one per cycle)

```bash
xcrun simctl io "$SIM_UDID" recordVideo \
  --codec=h264 \
  --mask=ignored \
  "audit-evidence/cycle-NN/run.mov" &
REC_PID=$!

# At end of cycle:
#   kill -SIGINT $REC_PID && wait $REC_PID
# SIGINT stops cleanly; SIGKILL corrupts the file.
```

h264 over HEVC for portability. The video is the safety net when a
screenshot is ambiguous.

## Launch the app

```bash
xcrun simctl launch "$SIM_UDID" "$BUNDLE_ID" 2>&1 \
  | tee audit-evidence/launch.log

sleep 2  # let first screen render
```

## Per-screen capture sequence

```bash
# Capture starting state
xcrun simctl io "$SIM_UDID" screenshot "$EV/dashboard-default.png"

# Capture accessibility tree (key for a11y findings)
xcrun simctl ui "$SIM_UDID" describe > "$EV/dashboard-accessibility.txt"
```

## Driving the app via deep links

```bash
# Navigate via custom URL scheme
xcrun simctl openurl "$SIM_UDID" "myapp://dashboard/new-session?name=test"

sleep 1
xcrun simctl io "$SIM_UDID" screenshot "$EV/journey-01-deeplink.png"
```

Deep links bypass UI navigation — useful for reaching specific states
without scripting an entire interaction sequence.

## Driving the app via accessibility actions

If the app exposes accessibility identifiers (best practice — request via
`accessibilityIdentifier` in code), you can activate elements directly:

```bash
xcrun simctl ui "$SIM_UDID" activate-accessibility-element \
  --bundle "$BUNDLE_ID" \
  --identifier "createButton"

sleep 1
xcrun simctl io "$SIM_UDID" screenshot "$EV/journey-01-after-tap.png"
```

If the app DOESN'T expose identifiers, you'll need to drive via
xcuitest-style automation OR rely on coordinate taps (brittle; avoid if
possible).

## Per-element state capture

Multi-state capture on iOS is less granular than web (no :hover). Capture:

- default
- selected (if cell-style)
- highlighted (mid-press) — via accessibility action
- disabled — via app-state manipulation
- loading — depends on app's loading-state design

iOS Buttons rendered via SwiftUI typically have built-in highlighted states
that animate on press. Activate via accessibility, screenshot mid-animation
(sleep 0.05 between activate and screenshot).

## Per-screen variant capture

Variants on iOS are driven by app state. Two common patterns:

### Pattern: Demo deep links

If the app supports `myapp://demo?state=empty`:

```bash
xcrun simctl openurl "$SIM_UDID" "myapp://demo?state=empty"
xcrun simctl io "$SIM_UDID" screenshot "$EV/dashboard-empty.png"
```

### Pattern: UserDefaults manipulation

```bash
xcrun simctl spawn "$SIM_UDID" defaults write "$BUNDLE_ID" \
  "demoState" "empty"
xcrun simctl terminate "$SIM_UDID" "$BUNDLE_ID"
xcrun simctl launch "$SIM_UDID" "$BUNDLE_ID"
sleep 2
xcrun simctl io "$SIM_UDID" screenshot "$EV/dashboard-empty.png"
```

Reset before exit: `xcrun simctl spawn "$SIM_UDID" defaults delete "$BUNDLE_ID" "demoState"`.

## Cross-mode capture

```bash
# Dark mode
xcrun simctl ui "$SIM_UDID" appearance dark
sleep 1
xcrun simctl io "$SIM_UDID" screenshot "$EV/dashboard-dark.png"
xcrun simctl ui "$SIM_UDID" appearance light

# Large text (Dynamic Type)
# Set via Settings app or via xcuitest
# Capture at .xxxLarge

# Reduced motion
# Settings > Accessibility > Motion > Reduce Motion = on
# Then launch / capture
```

## Phase 3 functional validation

```bash
# Pre-interaction
xcrun simctl io "$SIM_UDID" screenshot "$EV/journey-01-before.png"

# Drive interaction (deep link or accessibility activation)
xcrun simctl ui "$SIM_UDID" activate-accessibility-element \
  --bundle "$BUNDLE_ID" --identifier "createButton"

# Poll the accessibility tree for expected state
for i in $(seq 1 30); do
  xcrun simctl ui "$SIM_UDID" describe > /tmp/a11y-now.txt
  grep -q 'session-created-toast' /tmp/a11y-now.txt && break
  sleep 0.2
done

# Post-interaction
xcrun simctl io "$SIM_UDID" screenshot "$EV/journey-01-after.png"

# Verify backend call fired (if applicable)
# Tail the app log for the expected HTTP request line, OR
# Check the backend's log/DB for the corresponding mutation
```

## Cross-cycle regression diff

```bash
# Use ImageMagick to diff
compare -metric AE -fuzz 2% \
  "audit-evidence/cycle-01/dashboard-default.png" \
  "audit-evidence/cycle-02/dashboard-default.png" \
  "audit-evidence/cycle-02/diffs/dashboard-default-diff.png" 2>&1
# Output is the pixel count of differing pixels; threshold per cycle.
```

## Teardown per cycle

```bash
# Stop recording cleanly
kill -SIGINT $REC_PID
wait $REC_PID
ls -la audit-evidence/cycle-NN/run.mov  # confirm non-zero bytes

# Stop log stream
kill $LOG_PID

# Reset status bar
xcrun simctl status_bar "$SIM_UDID" clear

# Reset appearance
xcrun simctl ui "$SIM_UDID" appearance light
```

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Sleep-and-hope after activation | Race conditions | Poll accessibility tree for expected state |
| Coordinate taps | Layout shifts break them | Use accessibility identifiers |
| Skipping the log stream | Crashes invisible in screenshots | Always tail the app log alongside captures |
| HEVC video | Reviewers can't play it | Always h264 |
| Not capturing accessibility tree | a11y findings invisible | Always `simctl ui describe` per screen |
| `kill -9` on video recorder | Corrupts the file | Always SIGINT |

## Cross-references

- `skills/full-ui-experience-audit/` — parent skill
- `references/phase-0-setup.md` — iOS preflight
- `references/visual-experience-audit.md` — Phase 2 depth protocol
- `references/inventory-template.md` — Phase 1 output format
- `references/fix-loop-protocol.md` — Phase 4 fix discipline
- `skills/ios-validation-runner/` — deeper iOS validation patterns
- `skills/e2e-validate/references/ios-validation.md` — adjacent iOS-validation reference
