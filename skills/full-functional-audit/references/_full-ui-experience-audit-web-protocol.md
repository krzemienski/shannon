# Web Protocol

> agent-browser command sequences for Phase 2 (visual + interaction audit), Phase 3 (functional validation), and Phase 6 (clean confirmation pass) on web / fullstack projects.

## Why agent-browser (not Playwright)

Standardization rationale — see SKILL.md. Short version:
- Daemon persistence across cycles
- `@eN` refs survive DOM mutation better than CSS selectors
- Native MCP integration (tool calls land in transcript)
- Lower overhead than Playwright

If a doc says "use Playwright", translate to agent-browser before executing.

## Setup

```bash
# Start the dev server (or ensure it's running)
npm run dev > dev-server.log 2>&1 &
DEV_PID=$!
trap 'kill $DEV_PID' EXIT

# Wait for ready
for i in $(seq 1 60); do
  curl -sf "$BASE_URL" >/dev/null 2>&1 && break
  sleep 1
done

# Verify agent-browser daemon is up
agent-browser status
```

## Snapshot-then-act pattern (critical)

agent-browser refs (`@e1`, `@e2`, ...) are tied to a specific snapshot. They go stale on DOM mutation.

The rule: **snapshot immediately before every act**.

```bash
# WRONG — refs may be stale
agent-browser snapshot -i > /tmp/snap1.txt
# ... do other things, navigate, click, time passes ...
agent-browser click @e7   # @e7 may not exist anymore

# RIGHT — fresh snapshot for each act
agent-browser snapshot -i > /tmp/snap1.txt
agent-browser click @e7   # immediate, ref is fresh

# Then next act:
agent-browser snapshot -i > /tmp/snap2.txt
agent-browser fill @e3 'new value'
```

Stale-ref failures are the #1 source of false FAILs on web audits.

## Per-screen capture sequence

```bash
# Navigate
agent-browser navigate "$BASE_URL/dashboard"
sleep 0.5  # let initial render settle

# Capture default
agent-browser screenshot --output "$EV/dashboard-default.png"
agent-browser snapshot -i > "$EV/dashboard-default-snapshot.txt"

# Capture network log
agent-browser network > "$EV/dashboard-network.txt"

# Capture console
agent-browser console > "$EV/dashboard-console.txt"
grep -i 'error\|uncaught' "$EV/dashboard-console.txt" \
  >> "$EV/findings-console.txt"
```

## Per-element state matrix

For an interactive element in the inventory:

```bash
# Get fresh refs
agent-browser snapshot -i > /tmp/refs.txt

# Read refs to find the element; assume @e7 is the create-button

# Default
agent-browser screenshot --output "$EV/btn-create-default.png"

# Focus
agent-browser focus @e7
agent-browser screenshot --output "$EV/btn-create-focus.png"

# Hover
agent-browser hover @e7
agent-browser screenshot --output "$EV/btn-create-hover.png"

# Active (mid-press) — via CSS pseudo-class force
agent-browser exec 'document.querySelector("[data-action=create]").classList.add("active-pseudo")'
agent-browser screenshot --output "$EV/btn-create-active.png"
agent-browser exec 'document.querySelector("[data-action=create]").classList.remove("active-pseudo")'

# Disabled
agent-browser exec 'document.querySelector("[data-action=create]").disabled = true'
agent-browser screenshot --output "$EV/btn-create-disabled.png"
agent-browser exec 'document.querySelector("[data-action=create]").disabled = false'
```

## Per-screen variant capture

```bash
# Empty state
agent-browser navigate "$BASE_URL/dashboard?demo=empty"
agent-browser screenshot --output "$EV/dashboard-empty.png"

# Loading state (slow network)
agent-browser navigate "$BASE_URL/dashboard?demo=slow"
sleep 0.2  # catch mid-load
agent-browser screenshot --output "$EV/dashboard-loading.png"

# Overflow (many items)
agent-browser navigate "$BASE_URL/dashboard?demo=overflow"
agent-browser screenshot --output "$EV/dashboard-overflow.png"

# Error state
agent-browser navigate "$BASE_URL/dashboard?demo=error"
agent-browser screenshot --output "$EV/dashboard-error.png"

# First-launch (clear localStorage + reload)
agent-browser exec 'localStorage.clear(); sessionStorage.clear()'
agent-browser navigate "$BASE_URL/dashboard"
agent-browser screenshot --output "$EV/dashboard-first-launch.png"
```

If `?demo=*` query params aren't supported, add them as audit infrastructure
(they're cheap to add and pay back across many cycles).

## Cross-mode capture

```bash
# Dark mode
agent-browser exec 'document.documentElement.classList.add("dark")'
agent-browser screenshot --output "$EV/dashboard-dark.png"
agent-browser exec 'document.documentElement.classList.remove("dark")'

# Reduced motion
agent-browser exec '
  Object.defineProperty(window.matchMedia("(prefers-reduced-motion: reduce)"), "matches", {value: true});
  window.dispatchEvent(new Event("change"));
'
agent-browser screenshot --output "$EV/dashboard-reduced-motion.png"

# Large text (a11y)
agent-browser exec 'document.documentElement.style.fontSize = "20px"'
agent-browser screenshot --output "$EV/dashboard-large-text.png"
agent-browser exec 'document.documentElement.style.fontSize = ""'

# RTL
agent-browser navigate "$BASE_URL/dashboard?lang=ar"
agent-browser screenshot --output "$EV/dashboard-rtl.png"
```

## Phase 3 functional validation

```bash
# Interaction: click create-session button, verify backend call + UI update
agent-browser navigate "$BASE_URL/dashboard"
agent-browser snapshot -i > /tmp/refs.txt
# Identify create-button @eN from refs

# Capture pre-interaction state
agent-browser screenshot --output "$EV/journey-01-before.png"

# Capture network log snapshot
agent-browser network --clear   # reset log
agent-browser click @e7

# Wait for UI to update (poll, don't sleep — see anti-patterns)
for i in $(seq 1 30); do
  agent-browser snapshot -i > /tmp/refs-after.txt
  grep -q 'session created' /tmp/refs-after.txt && break
  sleep 0.2
done

# Capture post-interaction state
agent-browser screenshot --output "$EV/journey-01-after.png"
agent-browser snapshot -i > "$EV/journey-01-after-snapshot.txt"
agent-browser network > "$EV/journey-01-network.txt"

# Verify expected backend call fired
grep 'POST /api/sessions' "$EV/journey-01-network.txt" \
  || echo "FINDING: expected POST didn't fire"

# Verify UI updated to reflect the new session
grep -i 'session created' "$EV/journey-01-after-snapshot.txt" \
  || echo "FINDING: UI didn't show the new session"
```

## Cross-cycle regression diff

```bash
# In cycle 2+, diff against cycle-1 baseline
agent-browser diff screenshot \
  --baseline "audit-evidence/cycle-01/dashboard-default.png" \
  --candidate "audit-evidence/cycle-02/dashboard-default.png" \
  --tolerance 1% \
  --output "audit-evidence/cycle-02/diffs/dashboard-default-diff.png"
```

If `agent-browser diff screenshot` isn't available, fall back to ImageMagick `compare`.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Reusing a ref across multiple acts | Refs go stale | Fresh snapshot before each act |
| sleep-and-hope after click | Race conditions | Poll the snapshot for expected text |
| CSS selector in `exec` | Refactor breaks selector | Use refs from snapshot when possible |
| Skipping the network log | "UI looks right" but backend didn't fire | Always capture + verify network log |
| Skipping console errors | Errors hide bugs you'd otherwise see | Always grep console after each navigation |

## Cross-references

- `skills/full-ui-experience-audit/` — parent skill
- `references/phase-0-setup.md` — web preflight
- `references/visual-experience-audit.md` — Phase 2 depth protocol
- `references/inventory-template.md` — Phase 1 output format
- `references/fix-loop-protocol.md` — Phase 4 fix discipline
- `skills/agent-browser/` — full agent-browser reference
- `skills/e2e-validate/references/web-validation.md` — adjacent web-validation reference
