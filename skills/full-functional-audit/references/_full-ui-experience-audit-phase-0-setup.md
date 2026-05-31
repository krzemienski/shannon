# Phase 0 — Setup

> Pre-loop setup for full-ui-experience-audit. Six steps run before the audit loop starts. The setup is the loop's contract — without it, the loop has no source of truth.

## Step 1 — Write run-config.md

Single source of truth for the run. Every later phase reads from it.

```yaml
# audit-evidence/run-config.md (or YAML if you prefer)

app:
  name: "<app name>"
  platform: ios | web | fullstack | cross-platform   # user-declared; the
                                                       # table in SKILL.md is
                                                       # a hint, not authority
  base_url: "http://localhost:3000"                    # web/fullstack only
  sim_udid: "ABCDEF12-..."                             # iOS only
  bundle_id: "com.example.app"                         # iOS only

mode: solo | team
threshold: critical-only | critical-high | critical-high-medium | zero-defects
max_cycles: 10

coverage_axes:
  dark_mode: yes | no | not-supported
  accessibility: yes | no | not-supported
  i18n: yes | no | not-supported
  offline: yes | no | not-supported
  ...

degraded_mode: no | yes   # set yes if agent-browser unavailable
```

Coverage axis values: `yes` audits and counts toward full coverage; `no`
opts out but caps the verdict at `PASS (LIMITED COVERAGE)`; `not-supported`
means the feature genuinely doesn't exist (e.g., dark mode in a
single-theme app) and doesn't penalize the verdict.

## Step 2 — Generic preflight

Invoke the `preflight` skill if available. Verifies:
- Build green
- Backend reachable (for fullstack)
- Dev tools sane
- No stale processes hogging ports

If preflight fails: stop-the-world. The audit can't run against a broken
baseline.

If preflight skill isn't available, do the equivalent manually:

```bash
# Build
<build command for platform> 2>&1 | tee audit-evidence/preflight-build.log

# Backend (fullstack)
curl -sf "$BASE_URL/health" >/dev/null || echo "backend not reachable"

# Tools
command -v agent-browser >/dev/null || echo "agent-browser missing"
command -v xcrun simctl >/dev/null  || echo "xcrun missing"
```

## Step 3 — Platform-specific preflight

### Web

```bash
# Dev server reachable
curl -sf "$BASE_URL" | head -100 > audit-evidence/preflight-root.html

# agent-browser daemon up
agent-browser status > audit-evidence/preflight-browser-status.txt

# Console clean on startup
agent-browser navigate "$BASE_URL"
agent-browser console > audit-evidence/preflight-console.txt
grep -i 'error\|uncaught' audit-evidence/preflight-console.txt \
  && echo "preflight console errors — investigate before running audit"
```

### iOS

```bash
# Simulator boots
xcrun simctl bootstatus "$SIM_UDID" -b

# Build installs
xcrun simctl install "$SIM_UDID" "$APP_PATH"

# App launches
xcrun simctl launch "$SIM_UDID" "$BUNDLE_ID"
sleep 2
xcrun simctl io "$SIM_UDID" screenshot audit-evidence/preflight-launch.png
```

Read the preflight screenshot. If it shows error UI, ABORT — audit can't
distinguish pre-existing failures from regressions.

## Step 4 — Tool availability

Check every tool the loop will need:

```bash
for tool in agent-browser xcrun xcodebuild git jq curl repomix; do
  command -v $tool > /dev/null || echo "MISSING: $tool"
done
```

If a REQUIRED tool is missing, abort. If a NICE-TO-HAVE is missing (like
`repomix`), degrade gracefully (fall back to `grep` / `Glob`).

## Step 5 — Build the codebase index

```bash
# Preferred:
repomix --style xml --compress > audit-evidence/codebase.xml

# Fallback when repomix unavailable:
echo "repomix not installed; using direct grep against source tree"
```

The codebase index is consumed by Phase 1 (Discovery) to enumerate screens,
endpoints, and interaction surfaces.

## Step 6 — Baseline + evidence directory

```bash
mkdir -p audit-evidence/{baseline,cycle-01}

# Baseline screenshots — capture current-state BEFORE any audit work
# so pre-existing issues aren't blamed on the loop
agent-browser navigate "$BASE_URL"
agent-browser screenshot --output audit-evidence/baseline/root.png

# For each top-level route:
for route in / /dashboard /settings /profile; do
  agent-browser navigate "$BASE_URL$route"
  slug=$(echo "$route" | tr '/' '-' | sed 's/^-//;s/-$//')
  agent-browser screenshot --output "audit-evidence/baseline/${slug:-root}.png"
done

# iOS equivalent:
for view in main settings profile; do
  xcrun simctl openurl "$SIM_UDID" "myapp://$view"
  sleep 1
  xcrun simctl io "$SIM_UDID" screenshot "audit-evidence/baseline/$view.png"
done
```

The baseline is the comparison point for Phase 2 cycle-to-cycle visual
regression. Without baselines, you can't tell if a "new" finding is actually
pre-existing.

## Step 7 — (Implicit) Confirm with user

Before entering the loop, summarize the run-config back to the user and
confirm:

```
About to start full-ui-experience-audit:
  - App: <name>
  - Platform: <platform>
  - Mode: <solo | team>
  - Threshold: <threshold>
  - Max cycles: <N>
  - Coverage axes opted out: <list, if any>

Proceed? (Yes / Change config / Cancel)
```

If user changes config: re-write run-config.md, re-run any affected
preflight steps, then re-confirm.

## Output of Phase 0

After Phase 0:
- `audit-evidence/run-config.md` written
- `audit-evidence/preflight-*.log` captured
- `audit-evidence/baseline/*.png` captured
- `audit-evidence/codebase.xml` (or fallback artifacts) ready
- All required tools confirmed available
- User confirmation captured

The loop can now enter Phase 1.

## Cross-references

- `skills/full-ui-experience-audit/` — parent skill
- `references/visual-experience-audit.md` — sibling for Phase 2 visual depth
- `references/team-coordination.md` — sibling for team-mode setup
- `references/web-protocol.md`, `references/ios-protocol.md` — platform-specific protocols
- `references/inventory-template.md` — format for Phase 1's inventory.md output
- `skills/preflight/` — the standalone preflight skill
