# Fix-Loop Protocol

> Phase 4's algorithm for driving each finding to closed. The discipline that distinguishes "we logged 47 findings" from "we fixed 47 findings."

## Non-deferrable contract

Phase 4 fixes EVERY finding before Phase 5 evaluates convergence. "Log and continue past a Phase 3 FAIL" is not a legal move; the whole loop is built on the contract that Phase 4 closes findings.

If a finding genuinely can't be fixed in-cycle (third-party dependency, infrastructure outside reach), escalate to the user — don't silently defer.

## Priority ordering

Within a cycle, fix in this order:

```
CRASH > BACKEND > NAVIGATION > VISUAL > DATA > UX
```

Rationale:
- **CRASH**: blocks subsequent journeys; fix first
- **BACKEND**: integration failures hide multiple downstream bugs; fix second
- **NAVIGATION**: broken nav prevents reaching other findings
- **VISUAL**: rendering / contrast / layout
- **DATA**: list shows wrong count, badge wrong, etc.
- **UX**: copy / interaction-quality

Across severities: BLOCKING > HIGH > MEDIUM > LOW. Within severity, use the above category order.

## The 8-step fix algorithm

For each finding:

```
1. DIAGNOSE         Read source; trace code path; identify root cause
2. MOCK CHECK       If "let me mock this" tempted, invoke no-fakes-discipline
3. FIX              Minimal correct change
4. BUILD            Confirm it compiles / type-checks
5. RE-VALIDATE      Re-run the SPECIFIC Phase 2/3 step that failed
6. EVIDENCE         Invoke evidence-gate; cite specific evidence of the fix
7. COMMIT           One fix, one commit, descriptive message
8. NOTIFY (team)    Broadcast the fix in case other agents are affected
```

### Step 1 — DIAGNOSE

Read enough of the source to identify the root cause. Don't fix symptoms.

```
Finding: "Filter dropdown clips off-screen on narrow viewports."

Diagnose:
- Component file: src/components/FilterDropdown.tsx, line 47
- Root cause: dropdown uses `position: absolute; right: 0` without considering parent overflow
- Why it appears now: navbar was narrowed in last cycle; filter doesn't reflow

NOT root cause: "the dropdown is on the right" (that's the symptom; the
cause is the positioning strategy)
```

If you can't articulate the root cause in 1-2 sentences, you haven't
diagnosed deeply enough. Loop back to reading source.

### Step 2 — MOCK CHECK

If during diagnosis you find yourself thinking "let me mock the X" or "I'll stub the Y for now," STOP. Read `skills/no-fakes-discipline/` before proceeding.

The mock-temptation is a sign that:
- The real dependency is hard to reach (which is the actual bug)
- OR you don't understand the dependency well enough yet

Either way, don't mock. Address the underlying.

### Step 3 — FIX

Minimal correct change. Resist scope creep ("while I'm here..."). A surgical fix is easier to review, easier to revert, and less likely to introduce new findings.

```
Fix:
- Change `right: 0` to `right: clamp(0, 100% - dropdown-width, navbar-right)`
- One line, in one file
- No unrelated cleanup
```

If the fix legitimately requires multiple files / lines, that's fine. But if you find yourself "improving things you noticed while you were in there," extract those into separate commits AND separate findings.

### Step 4 — BUILD

Confirm the change compiles / type-checks / lints. Don't move to re-validation
with a broken build.

```bash
# Web
npm run build && npm run type-check && npm run lint

# iOS
xcodebuild -project ... build
```

If the build fails: fix the build, then come back to the finding. The build
failure is a NEW finding (regression — your fix broke compilation); track it.

### Step 5 — RE-VALIDATE

Re-run the specific Phase 2 / Phase 3 step that surfaced the finding. Not
the full audit — just the step.

```bash
# If the finding was a Phase 2 visual capture:
agent-browser navigate "$BASE_URL/dashboard"
agent-browser screenshot --output "$EV/post-fix/dashboard-narrow.png"
# Visually compare against the original problematic capture

# If the finding was a Phase 3 functional journey:
# Re-run that specific journey, capture pre/post evidence, verify expected outcome
```

If the re-validation still fails: the fix didn't address the root cause.
Loop back to Step 1.

### Step 6 — EVIDENCE

Invoke `evidence-gate` (or the Iron Rule transcript discipline). Don't claim
"fixed" without specific evidence.

```yaml
finding: F-c02-008
status: remediated
evidence:
  - before: audit-evidence/cycle-02/dashboard-filter-clipped.png
  - after:  audit-evidence/cycle-02/post-fix/dashboard-narrow.png
  - diff:   audit-evidence/cycle-02/diffs/filter-fix-diff.png
  - commit: <sha>
verification:
  - re-ran Phase 2 capture for narrow viewport
  - confirmed dropdown now contained within viewport
  - no new findings introduced
```

Evidence-without-citation is not evidence. Be specific.

### Step 7 — COMMIT

One fix per commit. Descriptive message:

```
fix(dashboard): contain filter dropdown within viewport on narrow widths

The filter dropdown used `position: absolute; right: 0` which let it
overflow when the parent container narrowed. Switching to `clamp()` keeps
it within the viewport.

Refs: audit-evidence/cycle-02 finding F-c02-008
Re-validation: audit-evidence/cycle-02/post-fix/dashboard-narrow.png
```

The commit message documents the diagnosis + fix + evidence. Future-you can
reconstruct the change.

### Step 8 — NOTIFY (team mode only)

In team mode, broadcast the fix to other agents working on related areas:

```yaml
notification:
  from: <agent-id>
  type: fix-applied
  finding: F-c02-008
  files_touched: ["src/components/FilterDropdown.tsx"]
  side_effects: "may affect any other component using FilterDropdown"
  action_requested: "if you're working on a screen that uses FilterDropdown, re-snapshot"
```

This prevents Agent B from concluding "the dashboard still has F-c02-008" because
they were working off a stale snapshot taken before Agent A's fix landed.

## Parallelization rules (team mode)

Apply the resource-mutex matrix from the SKILL.md:

```
Code edits to same file       → SERIAL (file-level mutex)
Code edits to different files
  in the same module          → CAUTION (cross-file refactors may collide)
Code edits to disjoint modules → PARALLEL (low collision risk)
Simulator interaction         → SERIAL (one tap at a time)
Browser interaction
  on same tab                 → SERIAL
  across tabs                 → PARALLEL
Curl on read endpoints        → PARALLEL
Curl on write endpoints       → SERIAL
```

When in doubt, serialize. False parallelism creates false failures.

## Stuck-state detection

If the same finding ID survives 2 consecutive Phase 4 attempts:

1. Mark as STUCK in `cycle-NN/findings.json`
2. Escalate to user with diagnostic:

```
F-c02-008 is stuck after 2 fix attempts.

Cycle 2 attempt 1: changed dropdown positioning to clamp() — still clipped.
Diagnosis: root cause may actually be in parent container's overflow rule,
not the dropdown itself.

User: do you want me to (a) investigate the parent, (b) accept the limitation
and document, or (c) defer to v7.1?
```

Don't grind on the same fix approach indefinitely. Stuck-state is a signal
to re-diagnose at a higher level.

## Regression detection

If a fix in Cycle N introduces a NEW finding in Cycle N+1:

1. The new finding gets a normal F-c0(N+1)-XXX ID
2. Add a `regression: F-c0N-YYY` tag pointing at the fix that introduced it
3. Phase 5's convergence check counts regressions specially — they're
   stronger signal than first-time findings (the fix process itself is leaking)

Two regressions in a row from the same fix area: re-evaluate the fix approach
at a higher level (refactor, redesign, or accept the limitation).

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Fix symptom instead of cause | Same class re-appears in another place | Diagnose root cause; document in commit |
| Multiple fixes in one commit | Can't revert one without all | Atomic commits — one fix per commit |
| "Quick mock to unblock" | Iron Rule violation | Address the real dependency or escalate |
| Skip re-validation | "Fix is obvious" | Always re-run the specific check that failed |
| Vague evidence ("now it works") | Future review can't verify | Cite specific captures / files / lines |
| Log-and-continue past CRITICAL | Phase 5 builds on Phase 4 having closed findings | Phase 4 is non-deferrable; fix or escalate |

## Cross-references

- `skills/full-ui-experience-audit/` — parent skill
- `references/phase-0-setup.md`, `inventory-template.md`, `visual-experience-audit.md` — sibling references
- `references/team-coordination.md` — team-mode coordination (mutex matrix)
- `references/web-protocol.md`, `references/ios-protocol.md` — platform-specific commands
- `skills/no-fakes-discipline/`, `skills/no-mocking-validation-gates/` — Step 2 references
- `skills/gate-validation-discipline/` — Step 6 evidence-gate enforcement
- `skills/root-cause-tracing/` — Step 1 deeper diagnosis
