# Defect Pattern Database

A catalog of common visual defects observed across Shannon validation runs, organized by symptom. Each entry includes the visible symptom, the root cause(s), the platforms it appears on, and the fix pattern.

Use this database when reviewing screenshots and a defect feels familiar — odds are the pattern is here. Citing the pattern by name in a verdict accelerates remediation.

## How to use

1. While walking the universal + platform checklist, when you spot a defect, scan this database for a matching pattern by SYMPTOM.
2. If found, cite the pattern code in the verdict: "FAIL — pattern V-007 (badge clipping). step-03-home.png, top-right corner."
3. The fix-pattern column gives the remediation approach; the consumer of the verdict can apply it without re-diagnosing.

## V-001 — Status bar overlap

| Field | Value |
|---|---|
| Symptom | Content visible behind / above the iOS status bar |
| Platforms | iOS, Catalyst |
| Root cause | View hierarchy ignores top safe area; `ignoresSafeArea(.all)` or `edgesIgnoringSafeArea(.all)` used without intent |
| Fix | Remove blanket `ignoresSafeArea`; use `.ignoresSafeArea(.container, edges: .bottom)` only when needed |
| Severity | BLOCKING |

## V-002 — Home indicator overlap

| Field | Value |
|---|---|
| Symptom | Tab bar or bottom button hidden behind the home indicator on Face-ID iPhones |
| Platforms | iOS Face-ID devices |
| Root cause | Bottom safe area not honored; fixed-height bottom bars without insets |
| Fix | Use `safeAreaInset(edge: .bottom)` or VStack with explicit Spacer + safeAreaInset |
| Severity | HIGH |

## V-003 — Truncated text in nav bar

| Field | Value |
|---|---|
| Symptom | Screen title shows as "Documen…" or similar mid-word truncation |
| Platforms | iOS, macOS, web |
| Root cause | Long localized title in a narrow nav bar; no minimumScaleFactor |
| Fix | Set `minimumScaleFactor(0.8)` on the title; consider abbreviated title for narrow widths |
| Severity | MEDIUM |

## V-004 — Pure white on dark background

| Field | Value |
|---|---|
| Symptom | Body text feels eye-searingly bright in dark mode |
| Platforms | iOS, macOS, web |
| Root cause | Hardcoded `#FFFFFF` instead of semantic `.label` / `var(--text-primary)` |
| Fix | Replace hex literal with semantic token; verify in both modes |
| Severity | HIGH |

## V-005 — Invisible focus ring

| Field | Value |
|---|---|
| Symptom | Cannot tell which element is keyboard-focused |
| Platforms | Web (most common), macOS |
| Root cause | `outline: none` or `outline: 0` applied globally without a replacement |
| Fix | Remove the global outline rule OR replace with `:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }` |
| Severity | BLOCKING |

## V-006 — Form fields missing labels

| Field | Value |
|---|---|
| Symptom | Form rendered with placeholders only; screen readers report "edit text" with no context |
| Platforms | Web |
| Root cause | `<input placeholder="Email">` without `<label>` |
| Fix | Add `<label for="email">Email</label>` above the input; placeholder can remain as a hint |
| Severity | HIGH |

## V-007 — Badge clipping container edge

| Field | Value |
|---|---|
| Symptom | Notification badge on a row icon extends past the rounded card corner |
| Platforms | iOS, web |
| Root cause | Badge positioned absolutely without parent `overflow: hidden` interaction, or zIndex out of order |
| Fix | Move badge inside the icon's overflow-clipping wrapper; or use sufficient padding around the icon |
| Severity | MEDIUM |

## V-008 — Sheet drag indicator missing

| Field | Value |
|---|---|
| Symptom | iOS bottom sheet with no visible "drag down to dismiss" affordance |
| Platforms | iOS |
| Root cause | Custom sheet without `.presentationDragIndicator(.visible)` |
| Fix | Add `.presentationDragIndicator(.visible)` or `.sheet` modifier with native presentation |
| Severity | MEDIUM |

## V-009 — Tap target under 44pt

| Field | Value |
|---|---|
| Symptom | A button or icon-tap appears too small for reliable touch |
| Platforms | iOS, web, Android |
| Root cause | Designer pixel-perfect icon at 24px without padding extension |
| Fix | Wrap the icon in a `Button` with explicit `.frame(minWidth: 44, minHeight: 44)`; web: `padding: 10px` to expand the click area |
| Severity | HIGH |

## V-010 — Doubled section spacing

| Field | Value |
|---|---|
| Symptom | Two large gaps between sections where one was intended |
| Platforms | iOS, web |
| Root cause | Both parent margin-bottom AND child margin-top set; or `.padding(.vertical, 24)` on a wrapper plus `.padding(.top, 16)` on its first child |
| Fix | Use a single margin source (top-only or bottom-only convention); audit the spacing system |
| Severity | LOW |

## V-011 — Hardcoded font size

| Field | Value |
|---|---|
| Symptom | Body text doesn't scale when Dynamic Type increased |
| Platforms | iOS |
| Root cause | `.font(.system(size: 14))` instead of `.font(.body)` |
| Fix | Replace literal sizes with semantic text styles (`.body`, `.headline`, `.caption`) |
| Severity | HIGH |

## V-012 — Glass card transparent in light mode

| Field | Value |
|---|---|
| Symptom | Card content appears to "float" without a visible container in light mode |
| Platforms | iOS, web |
| Root cause | `.thinMaterial` background works well in dark but lacks contrast on light; or low-opacity rgba |
| Fix | Use `.regularMaterial` in light contexts or layer a subtle border (1px hairline) |
| Severity | MEDIUM |

## V-013 — Loading state stuck

| Field | Value |
|---|---|
| Symptom | Spinner has been visible across multiple screenshots without resolution |
| Platforms | All |
| Root cause | No timeout on the async operation; or the spinner state is the "no data" empty state |
| Fix | Set explicit timeouts (5-10s) that transition to a real empty state with retry; never show indefinite spinner |
| Severity | HIGH |

## V-014 — Wrong tab selected after navigation

| Field | Value |
|---|---|
| Symptom | Bottom-tab indicator shows "Home" but content is the Search tab |
| Platforms | iOS, web |
| Root cause | TabView selection binding decoupled from route; or programmatic navigation set route without updating tab state |
| Fix | Bind tab selection to the same source of truth as the route; verify on every push/pop |
| Severity | HIGH |

## V-015 — Text contrast 3.4:1 on body copy

| Field | Value |
|---|---|
| Symptom | Body text feels low-contrast; passes "looks readable" but fails WCAG 4.5:1 |
| Platforms | Web, iOS |
| Root cause | Gray-on-white pair (`#777` on `#FFF` is 4.48:1 — just below the bar); or design system uses light text on light cards |
| Fix | Use `#666` or darker on white; verify with an automated contrast checker |
| Severity | HIGH |

## V-016 — Missing alt text on icon-as-button

| Field | Value |
|---|---|
| Symptom | A button rendered as just an icon — screen reader reads "button" with no context |
| Platforms | Web |
| Root cause | `<button><svg .../></button>` with no `aria-label` |
| Fix | `<button aria-label="Delete email"><svg .../></button>` |
| Severity | HIGH |

## V-017 — Modal traps focus after close

| Field | Value |
|---|---|
| Symptom | After dismissing a modal, Tab cycles in the now-hidden modal instead of the underlying page |
| Platforms | Web |
| Root cause | Focus-trap library not torn down on close; or `inert` attribute mismanaged |
| Fix | On close, return focus to the trigger element AND remove `aria-hidden`/`inert` from the rest of the page |
| Severity | BLOCKING |

## V-018 — Skeleton vs frozen content

| Field | Value |
|---|---|
| Symptom | A screen looks like real content but never updates (cached placeholder data shown as if real) |
| Platforms | Web, iOS |
| Root cause | Skeleton shimmer replaced with static placeholder; or initial data state never reconciled with fetched data |
| Fix | Use animated shimmer for skeletons; clear placeholder once real data arrives |
| Severity | HIGH |

## V-019 — Hover-only menu

| Field | Value |
|---|---|
| Symptom | A dropdown menu only opens on mouse hover; cannot be reached via keyboard or touch |
| Platforms | Web |
| Root cause | `:hover` CSS to show menu without `:focus-within` equivalent |
| Fix | Add `:focus-within` to the same selector; ensure menu opens on button click on mobile |
| Severity | HIGH |

## V-020 — Inconsistent button height

| Field | Value |
|---|---|
| Symptom | Two buttons side-by-side render at different heights due to inner content sizing |
| Platforms | Web |
| Root cause | Button uses `padding: 0.5em 1em` with content of different font sizes; or icon-vs-text mix |
| Fix | Fix button height as a design token (`min-height: 44px`); align inner content with flexbox |
| Severity | LOW |

## V-021 — Carousel with no pagination

| Field | Value |
|---|---|
| Symptom | Horizontal scrollable area has no dots or indicator showing "1 of N" |
| Platforms | iOS, web |
| Root cause | Custom horizontal ScrollView without pagination control |
| Fix | Add `PageTabViewStyle` on iOS; add `<nav role="tablist">` of pagination dots on web |
| Severity | MEDIUM |

## V-022 — Sticky header bleeds when scrolling

| Field | Value |
|---|---|
| Symptom | Sticky nav bar shows content "through" it during scroll because the bar has no backdrop |
| Platforms | Web |
| Root cause | `position: sticky` without a `background-color` |
| Fix | Add explicit background (white in light, dark-1 in dark); add a `backdrop-filter: blur(8px)` for glass effect |
| Severity | MEDIUM |

## V-023 — Auto-playing video with sound

| Field | Value |
|---|---|
| Symptom | Loading a page produces unexpected audio |
| Platforms | Web |
| Root cause | `<video autoplay>` without `muted` |
| Fix | Always pair `autoplay` with `muted`; allow user to unmute |
| Severity | HIGH |

## V-024 — Empty state shows "Loading…"

| Field | Value |
|---|---|
| Symptom | A list with zero items shows "Loading…" forever (no items will ever arrive) |
| Platforms | iOS, web |
| Root cause | Loading state and empty state share the same view; loading flag never flipped to false on empty success |
| Fix | Separate `loading`, `empty`, `error` states explicitly; transition to `empty` after successful fetch with no items |
| Severity | HIGH |

## V-025 — Mixed iconography

| Field | Value |
|---|---|
| Symptom | One screen has SF Symbols (single-line) next to custom icons (filled) — visual inconsistency |
| Platforms | iOS |
| Root cause | Multiple designers contributed different icon families; no shared icon set |
| Fix | Standardize on SF Symbols where available; commission missing icons in a single style |
| Severity | LOW |

## Adding new patterns

When you spot a defect not in this database three times across runs, propose a new entry:
1. Symptom (what you SEE in screenshots)
2. Platforms it appears on
3. Root cause from your investigation
4. Fix pattern
5. Suggested severity

Use the next sequential code (V-026, V-027...). Submit via PR against this file.
