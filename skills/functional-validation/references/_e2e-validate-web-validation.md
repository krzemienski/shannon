# Web Frontend Validation

> Real-system validation for web frontends: load real pages in a real browser, exercise real user interactions, capture real screenshots and DOM, verify backend integration. Default tool: `agent-browser` (not Playwright, not Puppeteer).

## Detection signals

A project is Web Frontend when ONE of these holds and backend handlers are absent (or treat as fullstack — see fullstack-validation.md):

| Framework | Marker | Dev command |
|-----------|--------|-------------|
| Next.js | `next.config.{js,ts}`, `app/` or `pages/` | `npm run dev` or `pnpm dev` |
| Vite | `vite.config.{js,ts}` | `npm run dev` |
| Create React App | `react-scripts` in package.json | `npm start` |
| Vue | `vue.config.js`, `.vue` files | `npm run serve` |
| Svelte / SvelteKit | `svelte.config.js`, `+page.svelte` | `npm run dev` |
| Angular | `angular.json` | `ng serve` |
| Astro | `astro.config.mjs` | `npm run dev` |
| Remix | `remix.config.js` | `npm run dev` |
| SolidStart | `app.config.ts` | `npm run dev` |
| Plain HTML | `index.html` at root | `python -m http.server` or any static server |

## Why agent-browser, not Playwright

Per Shannon v1 convention, web interactions go through `agent-browser`:

1. **Daemon persistence** — `agent-browser` keeps the browser session alive across validation cycles. Playwright/Puppeteer spawn a fresh browser per script invocation, losing state.
2. **Stable refs** — `agent-browser snapshot -i` returns `@e1`, `@e2`, … element refs that survive DOM mutations better than CSS-selector hardcodes.
3. **Native MCP integration** — wired into Claude Code's tool surface; the tool calls land in the validation transcript as evidence.
4. **Lower overhead** — no `--browser=chromium` flag thrashing, no node_modules dependency for Playwright.

If a referenced doc says "use Playwright", translate to agent-browser before executing. The patterns map:

| Playwright | agent-browser |
|------------|---------------|
| `await page.goto(url)` | `agent-browser navigate <url>` |
| `await page.click(selector)` | `agent-browser snapshot -i` → `agent-browser click @eN` |
| `await page.fill(selector, value)` | `agent-browser snapshot -i` → `agent-browser fill @eN '<value>'` |
| `await page.screenshot({path: 'x.png'})` | `agent-browser screenshot --output x.png` |
| `await page.locator(sel).textContent()` | `agent-browser snapshot -i` (read text from snapshot output) |

## Validation protocol

### Phase 1 — Start the dev server

```bash
npm run dev > e2e-evidence/dev-server.log 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null' EXIT

# Wait for readiness — poll the actual URL, don't sleep
for i in $(seq 1 60); do
  curl -sf http://localhost:3000 >/dev/null 2>&1 && break
  sleep 1
done
```

For static sites, `python -m http.server 3000` works too. Note the port the dev server uses (Next.js: 3000, Vite: 5173, Vue CLI: 8080, etc.).

### Phase 2 — Smoke test

```bash
# Load the root page
agent-browser navigate http://localhost:3000

# Capture snapshot (refs + visible text + structure)
agent-browser snapshot -i > e2e-evidence/smoke-snapshot.txt

# Capture screenshot
agent-browser screenshot --output e2e-evidence/smoke-root.png

# Check console for errors
agent-browser console > e2e-evidence/smoke-console.txt
grep -i 'error\|uncaught\|cannot read' e2e-evidence/smoke-console.txt \
  && { echo "console errors on smoke"; exit 1; }
```

**PASS:** page renders, no console errors. **FAIL:** white page, 404, console errors, network errors.

### Phase 3 — Per-screen journey

For each route / page identified in the plan, capture multi-state evidence:

```bash
# Navigate
agent-browser navigate http://localhost:3000/dashboard

# Default state
agent-browser screenshot --output e2e-evidence/dashboard-default.png
agent-browser snapshot -i > e2e-evidence/dashboard-default-snapshot.txt

# Interact — click a button
# First snapshot to get fresh refs:
agent-browser snapshot -i > /tmp/refs.txt
# Find the button by reading the snapshot text and identifying its @eN ref
agent-browser click @e7  # the create-session button

# Post-click state
agent-browser screenshot --output e2e-evidence/dashboard-after-click.png
agent-browser snapshot -i > e2e-evidence/dashboard-after-click-snapshot.txt

# Network log — verify a backend call fired
agent-browser network > e2e-evidence/dashboard-network.txt
grep 'POST /api/sessions' e2e-evidence/dashboard-network.txt \
  || { echo "expected backend call didn't fire"; exit 1; }
```

### Phase 4 — Visual + interaction states

For each interactive element on a screen, capture the state matrix:
- default
- hover (web only)
- focus (always — keyboard navigation)
- active
- disabled
- loading
- success
- error

```bash
# Focus the input
agent-browser snapshot -i  # find input ref
agent-browser focus @e5
agent-browser screenshot --output e2e-evidence/journey-form-focus.png

# Fill with invalid value, trigger error
agent-browser fill @e5 'bad@'
agent-browser snapshot -i > e2e-evidence/journey-form-error-snapshot.txt
agent-browser screenshot --output e2e-evidence/journey-form-error.png
grep -i 'invalid\|error\|required' e2e-evidence/journey-form-error-snapshot.txt \
  || { echo "validation error not shown"; exit 1; }

# Fill with valid value, trigger success
agent-browser fill @e5 'valid@example.com'
agent-browser click @e9  # submit button
agent-browser screenshot --output e2e-evidence/journey-form-success.png
```

### Phase 5 — Empty / loading / overflow states

Edge states are where most defects hide.

```bash
# Empty state — point to a route that has no data
agent-browser navigate http://localhost:3000/dashboard?demo=empty
agent-browser screenshot --output e2e-evidence/dashboard-empty.png

# Loading state — slow network simulation
# (agent-browser supports network-throttle if available; otherwise navigate and quickly screenshot)
agent-browser navigate http://localhost:3000/dashboard?demo=slow
sleep 0.2
agent-browser screenshot --output e2e-evidence/dashboard-loading.png

# Overflow state — many items
agent-browser navigate 'http://localhost:3000/dashboard?demo=overflow'
agent-browser screenshot --output e2e-evidence/dashboard-overflow.png
```

### Phase 6 — Cross-mode capture

Dark mode and reduced-motion are first-class citizens for accessibility:

```bash
# Dark mode (if the app supports it)
agent-browser navigate http://localhost:3000
agent-browser exec 'document.documentElement.classList.add("dark")'
agent-browser screenshot --output e2e-evidence/root-dark.png

# Reduced motion
agent-browser exec '
  Object.defineProperty(window.matchMedia("(prefers-reduced-motion: reduce)"),
    "matches", { value: true })
'
agent-browser navigate http://localhost:3000  # reload with the flag
agent-browser screenshot --output e2e-evidence/root-reduced-motion.png
```

### Phase 7 — Verdict

```
e2e-evidence/dashboard.verdict.md
---
**Journey**: GET /dashboard, click "Create Session", verify backend integration
**Expected**: page renders with empty state, click creates a session, dashboard shows it
**Observed**:
  - smoke: root page renders, no console errors ✓
  - empty state: empty-state.png shows "No sessions yet" copy ✓
  - click → POST /api/sessions fired (network log) ✓
  - response → dashboard shows 1 session card ✓
  - dark mode: contrast OK in dashboard-dark.png ✓
**Verdict**: PASS
**Evidence**: smoke-root.png, dashboard-empty.png, dashboard-after-click.png, dashboard-network.txt
```

## Static-only fallback (when agent-browser is unavailable)

If `agent-browser` isn't on PATH (degraded mode), drop to static analysis:

```bash
# Read the rendered HTML directly
curl -s http://localhost:3000 > e2e-evidence/static-root.html

# Grep for known affordances
grep -c '<button' e2e-evidence/static-root.html
grep -c 'role="button"' e2e-evidence/static-root.html

# Static contrast check via CSS inspection
grep -oE 'color:\s*#[0-9a-f]{3,6}' e2e-evidence/static-root.html | sort -u
```

Static analysis can catch contrast, missing-focus, false-affordance, and design-token drift without driving the browser. It cannot validate interactive behavior — those journeys mark FAIL with `degraded_mode: yes` rather than a false PASS.

## Iron Rule for web

NEVER add a mock for backend calls, route handlers, or third-party SDKs during web validation. If a backend is unavailable, start it (see api-validation.md). If a third-party SDK (auth, analytics) is required, use its real sandbox/test endpoint, not a local mock.

NEVER write `*.spec.ts`, `*.test.tsx`, or any test-harness file during validation. The validation IS the browser run; the evidence is screenshots + snapshots + network logs.

## Common anti-patterns

| Anti-pattern | Why it's wrong | Do this instead |
|--------------|----------------|------------------|
| Single screenshot per screen | Misses empty / loading / error states where most defects hide | Capture default + empty + loading + populated + error per screen |
| Validating happy path only | Real users hit edge cases | Force each edge state via URL params, query, or `agent-browser exec` |
| CSS selectors hardcoded across runs | DOM changes between renders break the selector | Use `agent-browser snapshot -i` for fresh @eN refs every interaction |
| No network-log inspection | Frontend "works" but doesn't call backend | `agent-browser network` after every interaction; verify expected requests |
| Skipping dark mode | Dark mode is where contrast bugs live | Always toggle dark + capture |
| Skipping the focus state | Keyboard users see different visuals | Always tab through focusable elements, capture each focus state |

## Cross-references

- `references/api-validation.md` — validate the backend the frontend hits
- `references/fullstack-validation.md` — composition order: DB → API → UI
- `skills/agent-browser/` — full agent-browser reference
- `skills/visual-inspection/` — per-screenshot QA protocol
- `skills/ui-experience-audit/` — 5-phase per-screen UX audit
- `skills/no-mocking-validation-gates/` — prevents the SDK-mock temptation
