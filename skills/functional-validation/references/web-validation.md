# Web Frontend Functional Validation

This reference is loaded by the `functional-validation` skill ONLY when the project is a browser-rendered web frontend (React, Vue, Svelte, Angular, plain HTML, Astro, Next.js, etc.). It expands the start/exercise/capture protocol for browser-based validation.

Do not load this file for purely server-side apps — use `api-validation.md`. For full-stack work, load this AND `api-validation.md`.

## The protocol at a glance

```
start backend (if any) -> start frontend dev/production server ->
navigate via agent-browser -> screenshot every state ->
read every screenshot -> verify network calls -> verdict
```

Web frontend validation is unique among the four platforms in that the rendered result depends not just on app code but on the browser, viewport, fonts, network conditions, and any HTTP intermediaries. Fix the variables you control; document the ones you don't.

## Detection signals (parent skill already checked)

| File present | Implication | Start command |
|---|---|---|
| `next.config.*` | Next.js | `npm run dev` -> http://localhost:3000 |
| `vite.config.*` | Vite | `npm run dev` -> http://localhost:5173 |
| `astro.config.*` | Astro | `npm run dev` -> http://localhost:4321 |
| `nuxt.config.*` | Nuxt | `npm run dev` -> http://localhost:3000 |
| `svelte.config.*` + `vite.config.*` | SvelteKit | `npm run dev` -> http://localhost:5173 |
| `angular.json` | Angular | `npm start` -> http://localhost:4200 |
| `package.json` with `"build":` and `"serve":` | Generic SPA | `npm run build && npm run serve` |
| `index.html` only | Static site | `python3 -m http.server` or `npx http-server` |

If the project is a Next.js or Nuxt SSR app, validate the production build too — `npm run build && npm run start`. SSR bugs (`window is not defined`, hydration mismatches) only appear in the production code path.

## Phase 1 — Start the frontend AND any backend it depends on

Frontend validation against a stubbed backend tests the stub, not the application. Start every dependency.

```bash
RUN_DIR="e2e-evidence/$(date +%Y-%m-%dT%H-%M-%S)/web-journey"
mkdir -p "$RUN_DIR"

# Start backend (if applicable) per api-validation.md
( cd backend && npm run dev ) > "$RUN_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
for i in $(seq 1 30); do
  curl -fsS http://localhost:3001/health >/dev/null 2>&1 && break
  sleep 1
done

# Start frontend
( cd frontend && npm run dev ) > "$RUN_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
FRONTEND_URL="http://localhost:3000"

for i in $(seq 1 60); do
  if curl -fsS "$FRONTEND_URL" >/dev/null 2>&1; then
    echo "Frontend ready"
    break
  fi
  sleep 1
done

# Verify the frontend actually serves the app shell, not a 502
curl -fsS "$FRONTEND_URL" -o "$RUN_DIR/initial-html.html"
grep -q '<div id="root"' "$RUN_DIR/initial-html.html" \
  || grep -q '<div id="app"' "$RUN_DIR/initial-html.html" \
  || echo "WARNING: initial HTML missing expected root element"
```

## Phase 2 — Drive the browser with agent-browser

`agent-browser` is the canonical Shannon tool for web validation. It runs a headless or headed Chromium controlled by JSON commands. Install via `npx agent-browser` if not already on PATH.

Standard journey shape: navigate -> wait for selector -> screenshot -> click/type -> wait -> screenshot -> repeat.

```bash
# Step 1: load the page
agent-browser navigate --url "$FRONTEND_URL/login" \
  --wait-for 'form[data-testid="login-form"]' \
  --screenshot "$RUN_DIR/step-01-login-loaded.png"

# Step 2: fill the form
agent-browser type --selector 'input[name=email]' --text 'user@example.com'
agent-browser type --selector 'input[name=password]' --text 'correct-horse-battery-staple'
agent-browser screenshot --output "$RUN_DIR/step-02-credentials-entered.png"

# Step 3: submit and wait for navigation
agent-browser click --selector 'button[type=submit]' \
  --wait-for 'h1[data-testid="dashboard-title"]' \
  --screenshot "$RUN_DIR/step-03-dashboard-loaded.png"
```

Use `data-testid` selectors when present — they survive design refactors. Fall back to ARIA roles (`role=button[name="Sign in"]`) before CSS class selectors. Never rely on text content alone for i18n apps.

For viewport-dependent behavior, set the viewport explicitly:

```bash
agent-browser viewport --width 375 --height 812   # iPhone 13 portrait
agent-browser viewport --width 1440 --height 900  # desktop
```

For dark/light mode verification, set `prefers-color-scheme`:

```bash
agent-browser emulate-media --color-scheme dark
agent-browser screenshot --output "$RUN_DIR/step-04-dashboard-dark.png"
agent-browser emulate-media --color-scheme light
agent-browser screenshot --output "$RUN_DIR/step-05-dashboard-light.png"
```

## Phase 3 — Capture the network

The network panel is the only honest record of what the page actually did. Capture it.

```bash
# Start network capture before the journey
agent-browser network record --output "$RUN_DIR/network.har"
# (run all navigate/click/type steps)
agent-browser network stop
```

After the run, inspect the HAR file for:
- Calls to URLs the page should NOT be calling (analytics in test mode, third-party trackers)
- Failed requests (4xx, 5xx, CORS, blocked-by-extension)
- Calls that returned correct status but wrong body
- Requests that the page issued multiple times unexpectedly

```bash
jq '.log.entries[] | select(.response.status >= 400) | {url: .request.url, status: .response.status}' \
  "$RUN_DIR/network.har" > "$RUN_DIR/failed-requests.json"

test -s "$RUN_DIR/failed-requests.json" \
  && { echo "FAIL: page issued failing requests"; cat "$RUN_DIR/failed-requests.json"; exit 1; } \
  || true
```

## Phase 4 — Capture the console

Browser console errors are equivalent to backend stack traces. Treat them with the same seriousness.

```bash
agent-browser console capture --output "$RUN_DIR/console.log"

# A clean run has NO console.error, NO unhandled promise rejections,
# and NO 404 from <link>/<img>/<script> tags.
grep -E '\[ERROR\]|Uncaught|Failed to fetch' "$RUN_DIR/console.log" \
  > "$RUN_DIR/console-errors.txt"

test -s "$RUN_DIR/console-errors.txt" \
  && { echo "WARNING: console errors detected"; cat "$RUN_DIR/console-errors.txt"; }
```

## Phase 5 — Verify

Run `visual-inspection` against every captured screenshot using the WCAG checklist (`references/web-wcag-checklist.md` in visual-inspection). Then:

1. **Read every screenshot.** Open with the Read tool. Describe what you see in one sentence. Compare to PASS criteria.
2. **Verify the network.** Every API call the page should have made, was made. No failing requests. No phantom requests.
3. **Verify the console is clean.** Zero errors, zero unhandled rejections.
4. **Verify the URL matches expectation.** Many "looks right" failures are actually "wrong route, similar-looking page."

```bash
# Get final URL
agent-browser url > "$RUN_DIR/final-url.txt"
test "$(cat "$RUN_DIR/final-url.txt")" = "$FRONTEND_URL/dashboard" \
  || { echo "FAIL: ended on wrong URL"; exit 1; }
```

Then invoke `evidence-gate` for the 6-question refusal-discipline pass.

## Production build validation

Dev-mode validation misses hydration mismatches, build-time tree-shaking errors, and CSS-in-JS extraction bugs. Run a separate production-build journey before declaring a release-ready PASS.

```bash
( cd frontend && npm run build && npm run start ) \
  > "$RUN_DIR/prod-server.log" 2>&1 &
PROD_PID=$!
sleep 5
# Repeat the journey against the prod server, output in a sibling dir
```

## Common web failure modes

| Symptom | Likely cause | Remedy |
|---|---|---|
| Screenshot is white | App didn't hydrate; JS error early in load | Check console for first error; increase `--wait-for` selector timeout |
| Click had no effect | Selector matched a hidden element | Use `agent-browser inspect --selector ...` to see the matched node |
| Element visible but click ignored | Modal overlay above it | Capture full-page screenshot to spot the overlay |
| Different result on retry | Race condition between API and render | Wait for the specific data, not just the container |
| Works in headed, fails in headless | Animation timing or video autoplay differences | Always validate headless; debug with headed only |
| 404 on `/static/*` resources | Wrong publicPath or base URL | Inspect built `index.html` for `<base>` tag and asset paths |
| Hydration mismatch error | SSR rendered different markup than client | Compare initial HTML to first-paint screenshot |

## When web path does NOT apply

- Browser extension — agent-browser cannot install extensions; validate via the extension test harness instead
- Print/CSS-only changes — use Puppeteer's `page.pdf()` to capture print output
- Service worker / offline behavior — combine with `--offline` mode and re-run the journey
- WebGL / Canvas-heavy apps — screenshots may be empty if the GPU pipeline failed; capture a `<canvas>` data URL via JS instead

## Evidence checklist

A PASS for a web feature requires at least:
- `initial-html.html` showing the page loaded
- One `step-NN-*.png` per meaningful state, READ by you
- `network.har` (or `failed-requests.json` empty)
- `console.log` with no errors
- `final-url.txt` matching the expected destination
- A `verdict.md` citing specific screenshots, network entries, and console state
- visual-inspection PASS per screenshot (WCAG checklist)
