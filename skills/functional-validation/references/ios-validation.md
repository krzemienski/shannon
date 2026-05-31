# iOS / macOS Functional Validation

This reference is loaded by the `functional-validation` skill ONLY when the project is iOS or macOS (detected by `.xcodeproj` or `.xcworkspace`). It expands the platform-specific build, launch, interaction, and evidence-capture sequence that the parent SKILL.md routes here.

Do not load this file for non-Apple projects.

## The protocol at a glance

```
boot simulator -> install app -> launch -> wait for first frame ->
exercise UI through xcrun simctl + AX tooling -> capture screenshots ->
read every screenshot -> verify against PASS criteria -> emit verdict
```

Five phases: SETUP, RECORD, ACT, COLLECT, VERIFY. Every phase produces evidence that lands under `e2e-evidence/<run-id>/<journey>/`.

## Detection signals (parent skill already checked)

| File present | Implication |
|---|---|
| `*.xcodeproj` at repo root | iOS or macOS Xcode project |
| `*.xcworkspace` | CocoaPods or SPM workspace — build via `-workspace` |
| `Package.swift` only | SwiftPM library or executable — not a UI app, downgrade to CLI route |
| `Info.plist` with `UIDeviceFamily` | Confirms iOS target |
| `Info.plist` with `LSUIElement` | macOS menu-bar app |

If the parent skill mis-routed and the project is a Swift library with no UI surface, fall back to the CLI reference and document the routing correction in `e2e-evidence/<run-id>/routing.md`.

## Phase 1 — SETUP

Boot the simulator BEFORE doing anything else. A cold simulator can take 30-60 seconds. Failing to wait results in screenshots of an empty home screen that you then mis-interpret as "app didn't launch."

```bash
# Pick a device. Use a fixed device for the run so screenshots are comparable.
DEVICE="iPhone 15 Pro"
SIM_UDID=$(xcrun simctl list devices "$DEVICE" available -j | \
  python3 -c "import json,sys;d=json.load(sys.stdin)['devices'];print([x['udid'] for v in d.values() for x in v if x['name']==\"$DEVICE\"][0])")

xcrun simctl boot "$SIM_UDID" 2>/dev/null || true   # idempotent
xcrun simctl bootstatus "$SIM_UDID" -b              # block until ready
open -a Simulator                                   # bring it to foreground
sleep 3                                             # let SpringBoard render
```

Verify the simulator is alive before proceeding:

```bash
xcrun simctl io "$SIM_UDID" enumerate 2>&1 | head -3
# Must print "Display: ..." — if empty, the sim is not ready.
```

If the project depends on a backend, start the backend AND poll its health endpoint until it returns 200. Do not proceed to the app until every dependency is healthy.

```bash
# Example backend health gate
( cd backend && npm run dev & )
for i in $(seq 1 60); do
  if curl -fsS http://localhost:3000/health >/dev/null 2>&1; then
    echo "Backend ready"
    break
  fi
  sleep 1
done
```

## Phase 2 — RECORD

Start screen recording AND log streaming before you touch the app. If the app crashes mid-journey, the recording is your only forensic trace.

```bash
RUN_DIR="e2e-evidence/$(date +%Y-%m-%dT%H-%M-%S)/login-journey"
mkdir -p "$RUN_DIR"

# Video — runs in background; killed in COLLECT phase.
xcrun simctl io "$SIM_UDID" recordVideo \
  --type=mp4 --force "$RUN_DIR/recording.mp4" &
VIDEO_PID=$!

# System log — capture only your bundle ID to keep file size sane.
BUNDLE_ID=$(/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" \
  "$(find build -name Info.plist -path '*.app/*' | head -1)" 2>/dev/null \
  || echo "com.example.app")
xcrun simctl spawn "$SIM_UDID" log stream \
  --predicate "subsystem == \"$BUNDLE_ID\"" \
  --style compact > "$RUN_DIR/console.log" &
LOG_PID=$!
```

## Phase 3 — ACT

Build, install, and launch the app from the same toolchain a real developer uses. NEVER skip the build step — a stale `.app` bundle hides regressions.

```bash
xcodebuild -workspace MyApp.xcworkspace \
  -scheme MyApp \
  -configuration Debug \
  -destination "id=$SIM_UDID" \
  -derivedDataPath build \
  build 2>&1 | tee "$RUN_DIR/build.log" | tail -20

# Verify build succeeded
test -d build/Build/Products/Debug-iphonesimulator/MyApp.app \
  || { echo "BUILD FAILED — see $RUN_DIR/build.log"; exit 1; }

xcrun simctl install "$SIM_UDID" \
  build/Build/Products/Debug-iphonesimulator/MyApp.app

xcrun simctl launch --console-pty "$SIM_UDID" "$BUNDLE_ID" \
  2>&1 | tee "$RUN_DIR/launch.log"
sleep 5  # let first frame render
```

For UI exercise, prefer accessibility-driven interactions over coordinate taps. Coordinates break on font-size changes and rotation; AX identifiers survive.

```bash
# Coordinate-based tap (brittle, last resort)
xcrun simctl io "$SIM_UDID" tap 200 400

# Preferred: AX-based via xcrun simctl + idb (if available)
idb ui tap --udid "$SIM_UDID" --label "Sign in"
idb ui type --udid "$SIM_UDID" "user@example.com"

# Deep link navigation — best when available
xcrun simctl openurl "$SIM_UDID" "myapp://login"
```

Between each action, sleep enough for animations and network requests to settle. Empirical rule: 1 second after tap, 3 seconds after navigation, 5+ seconds after first launch.

## Phase 4 — COLLECT

Take a screenshot AFTER every meaningful state change. Name files by step number — never by content — so failures are easy to trace.

```bash
for step in 01-launch 02-login-screen 03-credentials-entered 04-home-loaded; do
  xcrun simctl io "$SIM_UDID" screenshot "$RUN_DIR/step-${step}.png"
  test -s "$RUN_DIR/step-${step}.png" || \
    { echo "ZERO-BYTE screenshot — sim hung?"; exit 1; }
done

# Stop recording + log stream
kill "$VIDEO_PID" 2>/dev/null
kill "$LOG_PID" 2>/dev/null
wait
```

Capture the live UI tree at any critical step — far smaller than a screenshot, far easier to grep for missing labels.

```bash
xcrun simctl spawn "$SIM_UDID" \
  uitree dump > "$RUN_DIR/step-04-ui-tree.txt"
```

## Phase 5 — VERIFY

You MUST READ every screenshot before claiming PASS. File existence proves nothing — a screenshot of a crash dialog is still a .png file.

For each screenshot:
1. Open it with the Read tool (Claude can perceive PNG content directly).
2. Describe what is on screen in one sentence.
3. Compare against the PASS criteria you defined BEFORE the run.
4. Note any discrepancy. Discrepancies are either bugs or wrong criteria — never "good enough."

Cross-check with the console log. A green screenshot with red error log entries is a hidden failure.

```bash
grep -iE 'crash|fatal|error|exception' "$RUN_DIR/console.log" \
  | head -20 > "$RUN_DIR/log-warnings.txt"
```

Then invoke `visual-inspection` to run the iOS HIG checklist against each screenshot, and `evidence-gate` to apply the 6-question refusal-discipline checklist before declaring PASS.

## Common iOS failure modes

| Symptom | Likely cause | Remedy |
|---|---|---|
| Black screenshot | App didn't reach first frame; longer launch sleep needed | Increase post-launch sleep to 10s; check `launch.log` for missing entitlements |
| Screenshot of yesterday's app | Stale `.app` bundle from old build | Delete `build/`, rebuild |
| Tap registered but no UI change | Coordinate offset due to safe-area changes | Switch to AX identifier or deep link |
| "Cannot find simulator" | Wrong device name or version | `xcrun simctl list devices available` and pick from output |
| Launch immediately exits with code 0 | Background-mode app or test config error | Check `LSUIElement`, scheme args, debug config |
| Bundle ID mismatch on launch | Multiple targets in scheme | Hardcode bundle ID from Info.plist |
| Hang at "Building..." | Code signing prompt or pod install needed | Run `xcodebuild` once interactively to clear prompts |

## When iOS path does NOT apply

- Library-only Swift packages with no app target — use `cli-validation.md`
- Mac-Catalyst projects that target the desktop — same protocol but device list filters to macOS sims
- watchOS / tvOS — protocol works but device names differ; substitute device list accordingly
- Server-Swift (Vapor, Hummingbird) — use `api-validation.md`

## Evidence checklist

A PASS for an iOS feature requires at least:

- `build.log` ending in `** BUILD SUCCEEDED **`
- `launch.log` showing the launch process ID
- One `step-NN-*.png` per meaningful state, READ by you
- `console.log` checked for crash / fatal / exception lines
- A verdict file `verdict.md` citing each screenshot by relative path with line ranges where the verdict refers to log content
