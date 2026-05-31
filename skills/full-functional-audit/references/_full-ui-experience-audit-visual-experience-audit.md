# Visual Experience Audit

> Phase 2's depth protocol. Multi-state visual capture per element + screen-variant capture + cross-mode capture + cross-screen consistency audit. The phase that catches visual experience defects a single screenshot can't.

## Why a depth protocol

A single screenshot per screen catches the obvious. The non-obvious lives in:
- Hover / focus / active / disabled / loading / success / error states
- Empty / loading / populated / overflow / error / first-launch screen variants
- Dark mode + reduced-motion + i18n + RTL variants
- Cross-screen design-system consistency

The depth protocol surfaces these systematically.

## Per-element multi-state capture

For each interactive element in a screen's inventory row, capture every applicable state:

| State | What it shows | How to force |
|-------|---------------|--------------|
| default | Idle | Just navigate to the screen |
| hover (web only) | Mouse over | `agent-browser hover @eN` |
| focus | Keyboard focus | `agent-browser focus @eN` OR Tab key |
| active | Mid-press | Force via CSS inspection / `:active` pseudo |
| disabled | Element disabled | App state or `agent-browser exec` to set `disabled` attribute |
| loading | Mid-action | Trigger action; capture before completion |
| success | Post-action success | Trigger action, wait for success state |
| error | Post-action error | Trigger action with bad input |

Not every state applies to every element. A button has all 8; a static label has 1.

Capture commands:

```bash
# Web
agent-browser navigate "$BASE_URL/dashboard"
agent-browser snapshot -i > /tmp/refs.txt
# Identify the create-button by reading refs.txt; find its @eN

# Default
agent-browser screenshot --output "$DIR/btn-create-default.png"

# Focus
agent-browser focus @e7
agent-browser screenshot --output "$DIR/btn-create-focus.png"

# Hover
agent-browser hover @e7
agent-browser screenshot --output "$DIR/btn-create-hover.png"

# Disabled (force via exec)
agent-browser exec 'document.querySelector("[data-action=create]").disabled = true'
agent-browser screenshot --output "$DIR/btn-create-disabled.png"
```

## Screen-variant capture

Per screen, capture each variant:

| Variant | What | How to force |
|---------|------|--------------|
| empty | No data | New user, no items, or `?demo=empty` |
| loading | Mid-fetch | Throttled network OR `?demo=slow` |
| populated | Normal | Default state |
| overflow | Many items (10+, 100+) | `?demo=overflow` or seed test data |
| error | Backend failure | Backend off OR `?demo=error` |
| first-launch | New install | Reset app, capture first launch |

Variants surface bugs the populated state hides — "list works with 10 items but
breaks at 100", "loading state shows a flash of broken layout", "empty state
is blank where it should welcome the user."

State-forcing recipes for common frameworks:

| Framework | Empty | Slow | Error |
|-----------|-------|------|-------|
| React + MSW | `?demo=empty` mocked endpoint | `?demo=slow` with `delay()` | `?demo=error` returning 500 |
| Vanilla | URL query + conditional fetch | `setTimeout` wrap | `throw` in handler |
| iOS | UserDefaults flag | Charles proxy throttle | Mocked URLSession |

If state-forcing recipes aren't in place, ADD them. They're audit infrastructure.

## Cross-mode capture

For each screen, capture:

| Mode | When | How |
|------|------|-----|
| Light mode | Always | Default; no extra step |
| Dark mode | If `dark_mode: yes` in run-config | Toggle `prefers-color-scheme` |
| Reduced motion | If `accessibility: yes` | Override `prefers-reduced-motion` |
| Large text / a11y | If `accessibility: yes` | iOS: Settings > Accessibility > Text Size; Web: zoom |
| RTL | If `i18n: yes` and any RTL locale supported | Force locale to ar / he / fa |

These modes are where contrast bugs, layout overflow, and motion-issue bugs hide.

Capture commands:

```bash
# Dark mode (web)
agent-browser exec 'document.documentElement.classList.add("dark")'
agent-browser screenshot --output "$DIR/dashboard-dark.png"

# Reduced motion (web)
agent-browser exec '
  const mql = window.matchMedia("(prefers-reduced-motion: reduce)");
  Object.defineProperty(mql, "matches", { value: true });
  window.dispatchEvent(new Event("change"));
'
agent-browser screenshot --output "$DIR/dashboard-reduced-motion.png"

# RTL
agent-browser navigate "$BASE_URL/dashboard?lang=ar"
agent-browser screenshot --output "$DIR/dashboard-rtl.png"
```

## Cross-cycle visual regression

In cycles 2+, diff each capture against cycle-1's baseline:

```bash
# Web
agent-browser diff screenshot \
  --baseline "audit-evidence/cycle-01/$capture" \
  --candidate "audit-evidence/cycle-NN/$capture" \
  --tolerance 1%
# >1% pixel diff that isn't intentional = finding

# iOS
compare -metric AE \
  "audit-evidence/cycle-01/$capture" \
  "audit-evidence/cycle-NN/$capture" \
  "audit-evidence/cycle-NN/$capture-diff.png"
# AE (absolute error pixel count) above threshold = finding
```

Regression findings get a `regression` tag in `findings.json` and are
investigated specially — they imply something in cycle N's fixes broke a
previously-working state.

## Cross-screen consistency audit

After per-screen audits, run ONE consistency pass per cycle:

### Token consistency
- All primary buttons use the same color value
- All section headings use the same type scale
- All cards use the same border radius / shadow

```bash
# Extract color tokens from rendered HTML
grep -oE 'background-color:\s*rgb\([^)]+\)' audit-evidence/cycle-NN/*.html \
  | sort -u > audit-evidence/cycle-NN/colors-found.txt

# Compare against design-system spec
diff audit-evidence/cycle-NN/colors-found.txt design-system/allowed-colors.txt
```

### Component shape consistency
- All modals have the same close-button position
- All forms use the same submit-button placement
- All empty states use the same copy + illustration pattern

### Nav continuity
- Same nav appears in every screen's nav area
- Active state is consistent
- No "dead" nav items

### Iconography contact sheet
- Generate a sheet of all icons used in the app
- Visual scan for inconsistency (different styles, sizes, weights)

The cross-screen audit catches design-system drift — the bugs no single
screen audit can. Drift is usually CRITICAL or HIGH because it's expensive
to fix later (touches many screens).

## Static-mode visual grep playbook (degraded mode)

When `agent-browser` isn't available, fall back to static analysis:

```bash
# Contrast check — extract foreground/background pairs and compute ratio
# Run a contrast-check script against rendered HTML/CSS

# Touch target size — find all interactive elements; check height/width
grep -E '<button|role="button"' "$DIR/*.html" | extract sizes

# Focus visibility — search for `:focus` rules in CSS
grep ':focus' "$DIR/*.css"

# Design-token drift — extract every CSS color value; check against allowed set
grep -hoE '#[0-9a-fA-F]{3,6}|rgb\([^)]+\)' "$DIR/*.{css,html}" | sort -u
```

Degraded mode catches the bugs that don't require live driving — usually
contrast, false-affordance, missing-focus, design-token drift. Catches less
than live driving, but >0 is still useful.

## Output of Phase 2

Per cycle:
- `cycle-NN/captures/{screen-slug}-{state}.png` — multi-state captures
- `cycle-NN/captures/{screen-slug}-{variant}.png` — variant captures
- `cycle-NN/captures/{screen-slug}-{mode}.png` — mode captures
- `cycle-NN/diffs/{capture}-diff.png` — regression diffs (cycle 2+)
- `cycle-NN/consistency-report.md` — cross-screen audit findings
- Appended to `cycle-NN/findings.json` with `phase: "ux"` per finding

## Cross-references

- `skills/full-ui-experience-audit/` — parent skill
- `references/phase-0-setup.md` — what enables Phase 2 (baseline + tooling)
- `references/inventory-template.md` — what Phase 2 reads to know what to capture
- `references/web-protocol.md`, `references/ios-protocol.md` — platform-specific commands
- `skills/ui-experience-audit/` — single-screen UX audit invoked per screen
- `skills/visual-inspection/` — per-screenshot QA invoked from inside Phase 2
