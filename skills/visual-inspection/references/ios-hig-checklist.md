# iOS / macOS Apple HIG Checklist

Load this checklist when reviewing any screenshot from an Apple-platform target. It expands the universal checklist in `visual-inspection/SKILL.md` with Apple-platform-specific concerns drawn from Apple's Human Interface Guidelines.

Apply these in addition to the universal checklist — never as a replacement.

## Why HIG matters

Apple's HIG is the de facto standard users have been trained on for decades. Violations don't just look wrong — they feel wrong, slow users down, and trigger app rejections during App Review. A screen that "works" but breaks HIG fundamentals is not PASS.

## Touch targets and tap geometry

- [ ] Minimum tap target is 44pt × 44pt — the HIG floor for an adult fingertip
- [ ] No two interactive elements share an edge with less than 8pt separation
- [ ] Buttons inside lists provide at least 60pt row height
- [ ] Toolbar / tab bar buttons have visible padding around their icon — the tap target extends beyond the visible icon
- [ ] Swipe-to-act handles do not occupy the trailing edge of a scrollable list (conflict with edge-swipe-to-back)
- [ ] Drag handles appear in the leading or trailing safe area, never in the middle of a row

## Navigation bar and back-stack

- [ ] The back button uses the system chevron (`chevron.backward`) — not a custom asset
- [ ] Back button title shows the previous screen's title, truncated if needed
- [ ] Large titles (`prefersLargeTitles=true`) collapse smoothly into compact on scroll
- [ ] No nav-bar-overlay-on-content — content scrolls UNDER the nav bar, not under fixed gradient
- [ ] Search bar uses `UISearchController` or `.searchable()` — not a hand-rolled text field
- [ ] Trailing nav items follow icon-only convention; only one text label maximum

## Safe areas and edges

- [ ] No content under the status bar (top safe area)
- [ ] No content under the home indicator (bottom safe area on Face-ID devices)
- [ ] Sidebar / split-view content respects readable width on iPad
- [ ] Landscape orientation honors safe areas on both sides (notch / dynamic island)
- [ ] First-and-last list cells have padding to the safe-area edge, not hugging it

## Typography and text styles

- [ ] Body text uses `.body` / `.title` / `.headline` semantic text styles, NOT hardcoded 14pt
- [ ] Text scales with Dynamic Type — verify by enabling AX1 → AX5 in simulator and re-screenshotting
- [ ] No system fonts mixed with custom fonts in the same hierarchy (button label + body using different families)
- [ ] Monospace digits used for counters, timers, and tabular data
- [ ] Headlines use semibold (or bold) weight; body uses regular weight
- [ ] Tracking and leading match SF Pro defaults — no negative letter-spacing on body copy

## Color and contrast

- [ ] System colors (`.systemBackground`, `.label`, `.secondaryLabel`, `.systemBlue`) used — not hex literals
- [ ] Asset catalog supplies dark variants for every custom color
- [ ] Text contrast ≥ 4.5:1 normal, ≥ 3:1 large (18pt+)
- [ ] Tint color used consistently for interactive elements
- [ ] No color used as the SOLE differentiator (e.g., "red is the error state" without an icon)
- [ ] Vibrancy effects (`.thinMaterial`, `.regularMaterial`) used in correct backdrops

## SF Symbols

- [ ] Custom artwork only when an SF Symbol does not exist for the concept
- [ ] Symbol weights match adjacent text weight (`.regular`, `.medium`, `.semibold`)
- [ ] Scales (`.small`, `.medium`, `.large`) chosen by context — list icons `.medium`, tab-bar `.large`
- [ ] Multicolor / hierarchical / palette modes used per HIG guidance (status icons use multicolor)
- [ ] Custom-rendered symbols include all four weight variants

## Layout and spacing

- [ ] Section spacing matches list style (insetGrouped: 35pt between sections, plain: 22pt)
- [ ] Cell margins use `.contentMargins(.horizontal, X)` — not hand-tuned `.padding`
- [ ] Horizontal spacing follows 8-pt grid (8, 16, 24, 32)
- [ ] Cards have at least 16pt internal padding on all sides
- [ ] Edge-to-edge images use full bleed; bordered images use 16pt outer margin

## Lists and tables

- [ ] List style matches semantics — `.insetGrouped` for settings, `.plain` for timelines, `.sidebar` for navigation
- [ ] Disclosure indicators appear on rows that push a destination
- [ ] Swipe actions follow leading-trailing semantics (destructive trailing red, secondary leading)
- [ ] Empty state shows a meaningful illustration + headline + body, not just blank space
- [ ] Pull-to-refresh present on lists where the data is server-backed

## Sheets, popovers, and modal presentations

- [ ] Sheets use `.presentationDetents` to allow medium and large stops
- [ ] Drag indicator (`Capsule()` handle) visible on medium-detent sheets
- [ ] Cancel button on the leading edge; primary action on the trailing edge
- [ ] Modal presentation never replaces a navigation push for stack-style flows
- [ ] iPad popovers anchor to the triggering element with an arrow
- [ ] Full-screen covers reserved for immersive flows (camera, video, onboarding)

## Forms and input

- [ ] Keyboard type matches the field (numeric for digits, email for email)
- [ ] `submitLabel` set on each field for the right return-key text
- [ ] Field focus visible — system blue ring or label color change
- [ ] Validation errors appear inline below the field, not in an alert
- [ ] Form scroll keeps focused field visible above the keyboard

## Alerts and confirmations

- [ ] Alert title is a short statement, body is the explanation
- [ ] Destructive actions tagged `.destructive` (renders red)
- [ ] Cancel is always present for destructive confirmations
- [ ] No alerts used for non-blocking information — use toasts or notification banners
- [ ] Confirmation dialogs (`.confirmationDialog`) used for action sheets on iOS

## Animations and motion

- [ ] Default spring animations used (`.spring(response: 0.4, dampingFraction: 0.8)`)
- [ ] Reduce Motion accessibility setting honored — disable parallax / shake animations
- [ ] Transitions match navigation semantics (push slides horizontally, sheet slides vertically)
- [ ] No spinner that never stops — every spinner has a timeout state

## Accessibility

- [ ] Every interactive element has an accessibility label
- [ ] Labels describe action, not appearance — "Delete email" not "Trash icon"
- [ ] Custom controls expose `accessibilityValue` and `accessibilityHint` where helpful
- [ ] VoiceOver focus order matches visual reading order
- [ ] Color blindness — interaction still distinguishable when desaturated
- [ ] `.accessibilityElement(children: .ignore)` used on decorative composite views

## Dark mode pitfalls

- [ ] No pure white (`#FFFFFF`) on dark — use `.label` / `.secondaryLabel`
- [ ] Glass/blur backgrounds use `.thinMaterial`, not transparent solid colors
- [ ] Shadows reduced or removed in dark mode (use border or background contrast instead)
- [ ] Image-on-color overlays remain legible when the underlying color flips
- [ ] Status indicators visible in both modes (a yellow dot is invisible on light backgrounds)

## iPad-specific

- [ ] Sidebar uses `NavigationSplitView` — not `NavigationView` with a master/detail hack
- [ ] Split view supports column resizing; minimum widths set
- [ ] Multitasking states (slide-over, split-view) render reasonably at narrow widths
- [ ] Keyboard shortcuts (`⌘N`, `⌘S`, etc.) available where appropriate
- [ ] Hover state defined for pointer interactions (mouse / trackpad)

## macOS-specific (when target is Catalyst or AppKit)

- [ ] Window controls (traffic lights) present and functional
- [ ] Toolbar customizable via menu
- [ ] Menu bar items follow Edit / File / View / Window / Help structure
- [ ] Right-click context menus mirror primary actions
- [ ] Drag-and-drop into and out of the window works for relevant items

## When to fail and when to log

| Severity | Examples | Action |
|---|---|---|
| BLOCKING | Status bar overlap, illegible text, tap target < 44pt on primary action | Fail the screen; remediate before commit |
| HIGH | Wrong nav-bar back style, no dark-mode variant, missing AX labels | Fix in same session; do not ship |
| MEDIUM | Hardcoded color instead of system color, spacing off by 4pt | Track and fix; do not block release |
| LOW | Mixed SF Symbol weight, missing `accessibilityHint` | Log to design backlog |

## Citation discipline

For every failure logged, cite the screenshot file path AND describe the failing region in words: "step-03-home-loaded.png, top-right corner — badge clips the rounded card edge by ~4pt." File existence is not enough; the reader needs to find the defect without re-running the test.
