# Web WCAG 2.2 Checklist

Load this checklist when reviewing any screenshot from a browser-rendered target. It expands the universal checklist in `visual-inspection/SKILL.md` with web-specific concerns aligned with WCAG 2.2 Level AA.

Apply these in addition to the universal checklist — never as a replacement.

## Why WCAG matters

WCAG is more than an accessibility floor. Compliance signals quality across the entire visual + interactive surface — contrast, focus, motion, text sizing — that benefit every user. A screen that "looks fine" but fails contrast or keyboard navigation is not PASS.

## Contrast (1.4.3, 1.4.6, 1.4.11)

- [ ] Body text contrast ≥ 4.5:1 against its background (computed, not "looks dark enough")
- [ ] Large text (18pt regular or 14pt bold) ≥ 3:1
- [ ] Non-text content (icons, focus rings, borders) ≥ 3:1 against adjacent colors
- [ ] Placeholder text contrast ≥ 4.5:1 — the most commonly missed (gray-on-gray)
- [ ] Disabled controls visibly distinct from enabled AND still readable
- [ ] Text over images uses a scrim, overlay, or guaranteed-background container
- [ ] Tested in BOTH light and dark modes — defaults often fail one

## Focus visibility (2.4.7, 2.4.11)

- [ ] Every interactive element has a visible focus indicator when reached via Tab
- [ ] Default browser focus ring NEVER removed without a replacement
- [ ] Focus indicator contrast ≥ 3:1 against the focused element AND its background
- [ ] Focus indicator at least 2px thick or equivalent
- [ ] Focus moves in a logical order matching the visual layout
- [ ] No "focus trap" except in explicit modal dialogs (which must trap)
- [ ] Skip-to-content link present on long pages and reachable from the first Tab

## Keyboard operability (2.1)

- [ ] Every interactive element reachable via Tab (no `tabindex="-1"` on user-action elements)
- [ ] Custom controls (sliders, switches, comboboxes) respond to arrow keys per ARIA pattern
- [ ] Esc closes modals, popovers, dropdowns
- [ ] Enter activates the primary action; Space toggles checkboxes / switches
- [ ] No keyboard "trap" outside legitimate modal context
- [ ] Mouse-only affordances have keyboard equivalents (hover menus must also work on focus)

## Touch targets (2.5.5, 2.5.8)

- [ ] Minimum 24px × 24px (WCAG 2.2) — though 44px × 44px is recommended
- [ ] At least 24px spacing between adjacent targets, or larger
- [ ] Adjacent links/buttons in compact navigation provide padding
- [ ] Form input fields visually grouped from their labels (labels click-activate the field)

## Text and reading

- [ ] Body line-height ≥ 1.5
- [ ] Paragraph spacing ≥ 1.5x font size
- [ ] Letter spacing ≥ 0.12x font size where applied
- [ ] Word spacing ≥ 0.16x font size where applied
- [ ] No justified text (causes river-of-white gaps that hurt readability)
- [ ] Maximum line length around 80 characters for body copy
- [ ] Text remains readable at 200% browser zoom
- [ ] No horizontal scroll appears at 320px width (reflow per 1.4.10)

## Forms

- [ ] Every input has a visible `<label>` associated via `for=`/`id` or wrapping
- [ ] Placeholder text never substitutes for a label
- [ ] Required fields marked with both text ("Required") and visual indicator
- [ ] Inline validation error messages appear below the field, not above
- [ ] Error messages describe the problem AND the fix
- [ ] Error fields visually distinguished with a 3:1 contrast border, not just red
- [ ] Submit button label describes the action ("Sign in", not "Submit")
- [ ] Autocomplete attributes (`autocomplete="email"`, etc.) present on common fields

## Headings and structure

- [ ] Exactly one `<h1>` per page (or one per landmark in SPA layouts)
- [ ] Heading levels do not skip (h1 → h2 → h3, never h1 → h3)
- [ ] `<main>`, `<nav>`, `<aside>`, `<footer>` landmarks present
- [ ] Lists marked up as `<ul>`/`<ol>` — not just visually styled divs
- [ ] Tables include `<th>` for header cells, `scope=` attribute when ambiguous
- [ ] Form sections use `<fieldset>` + `<legend>` for grouped inputs

## Images and media

- [ ] Every meaningful image has `alt` text describing the content
- [ ] Decorative images have `alt=""` (empty string, not missing)
- [ ] Icons-as-buttons have an `aria-label` describing the action
- [ ] Charts and infographics have a text alternative (table, summary, longer description)
- [ ] Video has captions; audio has a transcript
- [ ] `prefers-reduced-motion` honored — animations disable or reduce
- [ ] Auto-playing video has no audio (or is muted) and can be paused

## Color use

- [ ] Color never the SOLE differentiator for status, errors, or required-fields
- [ ] Links underlined or otherwise distinguished from body text (not just color)
- [ ] Charts use patterns + color, not color alone, to distinguish series
- [ ] Form validation errors include an icon + text, not just red border

## Motion and animation

- [ ] No flashing content faster than 3 times per second
- [ ] Parallax / large-area scroll animations disable when `prefers-reduced-motion: reduce`
- [ ] Autoplay carousels respect reduced motion AND offer pause control
- [ ] Hover/focus animations are subtle (under 200ms) and never disorienting

## Internationalization

- [ ] `<html lang="...">` set to the page's primary language
- [ ] Sections in a different language carry `lang` attribute
- [ ] Layouts don't break in right-to-left (RTL) mode if the app supports it
- [ ] Numbers, dates, times formatted via `Intl` not string templates
- [ ] Long-text-language overflow handled (German labels often 2x English length)

## Loading and feedback

- [ ] Skeleton screens or shimmer effects show during initial load — not blank space
- [ ] Loading spinners include text ("Loading…") for screen readers
- [ ] Operations longer than 1s show progress feedback
- [ ] Long forms persist user input between page navigations
- [ ] Save / submit shows a confirmation toast or inline indicator
- [ ] No "Are you sure?" prompts for reversible actions

## Modal dialogs

- [ ] Triggered by user action — never automatically
- [ ] Focus moves into the modal on open; returns to trigger on close
- [ ] Esc closes the modal
- [ ] Clicking outside the modal closes it (unless explicitly modal-required)
- [ ] Background scroll locked
- [ ] Modal has `role="dialog"` + `aria-labelledby` pointing to its title

## Notification patterns

- [ ] Toasts disappear after 5–10s, with explicit dismiss
- [ ] Banners persist until dismissed
- [ ] Alerts (high-priority) require user action
- [ ] All notifications announced via `aria-live` for screen readers

## Responsive layout

- [ ] Layout works at 320px, 768px, 1024px, 1440px viewport widths
- [ ] No horizontal scrollbar at supported widths
- [ ] Tap targets remain ≥ 24px even at compressed widths
- [ ] Images scale via `srcset` or `picture` for resolution-appropriate fetching
- [ ] Tables either stack or scroll horizontally on narrow widths — never truncate

## Dark mode

- [ ] System preference detected via `prefers-color-scheme`
- [ ] Manual toggle persists across reloads (localStorage)
- [ ] Inputs, charts, embedded media all switch — not just text and background
- [ ] Brand colors adjusted for dark mode (often lighter / desaturated)
- [ ] Shadows reduced or replaced with borders in dark
- [ ] Status colors (success green, error red) tuned for dark backgrounds

## Print

- [ ] `@media print` styles tested for any print-able view
- [ ] Page breaks avoid splitting headings from their content
- [ ] Background colors removed for ink savings
- [ ] URL of page printed at the top or bottom

## When to fail and when to log

| Severity | Examples | Action |
|---|---|---|
| BLOCKING | Body text contrast < 4.5:1, focus invisible, modal traps focus permanently | Fail the screen; remediate before commit |
| HIGH | Missing form labels, missing alt text, color-only error indication | Fix in same session; do not ship |
| MEDIUM | Heading-level skip, line-height < 1.5, missing autocomplete attrs | Track and fix; do not block release |
| LOW | Missing `lang` on minority-language section, suboptimal touch spacing | Log to a11y backlog |

## Citation discipline

For every failure logged, cite the screenshot file path AND describe the failing region: "step-04-checkout.png, primary submit button — focus ring removed by `outline: none` declaration, no replacement provided." Generic notes like "contrast looks low" are not actionable.
