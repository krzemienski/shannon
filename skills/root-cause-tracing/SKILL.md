---
name: root-cause-tracing
description: Five-whys cascade plus Ishikawa cause-and-effect diagram for root cause analysis. BEFORE/AFTER reality-check state documentation. VF task injection for fix-type plans. ALWAYS use when the user says "why is X happening", "root cause", "five whys", "cause and effect", "fishbone analysis", or invokes /shannon:why or Phase 2 of /shannon:fix. Produces an analysis report with cited evidence per "why" layer plus a reproduction baseline.
triggers:
  - "why is X happening"
  - "root cause"
  - "five whys"
  - "cause and effect"
  - "fishbone analysis"
---

# root-cause-tracing

Backs `/shannon:why` and Phase 2 of `/shannon:fix`. Five-whys cascade plus Ishikawa categorization, merged with ralph-specum/reality-verification's BEFORE/AFTER pattern + VF task injection + command-mapping table + mock-quality red flags.

## Behavior contract

1. Read symptom description.
2. **Goal detection**: classify as Fix vs Add. Fix triggers BEFORE/AFTER state documentation.
3. **BEFORE state (reality check)**: reproduce the failure with the canonical command (see command-mapping table). Capture the verbatim failure output in `reports/root-cause-<slug>.md` and `.progress.md`.
4. **Apply five-whys**: each "why" probes one level deeper. Stop when an actionable root cause is reached (not "it's complicated").
5. **Build cause-and-effect diagram** (Ishikawa fishbone) categorizing across:
   - **Code** — logic error, race condition, type mismatch, edge case
   - **Data** — bad input, schema drift, missing record, stale cache
   - **Config** — wrong env var, misconfigured route, missing secret
   - **Environment** — OS/runtime version, network, hardware constraint
   - **Dependency** — library bug, version mismatch, broken upstream
   - **Human** — incorrect assumption, missed step, undocumented constraint
6. Identify primary category + minimal fix.
7. Inject a **VF (verify-fix) task** into the downstream plan that will re-run the reproduction command after the fix and assert AFTER state shows resolution.
8. Write `reports/root-cause-<slug>.md` with BEFORE state, five-whys chain, fishbone diagram, recommended fix, VF task.

## Command-mapping table (reproduction)

| Goal keywords | Reproduction command |
|---|---|
| CI, pipeline, GitHub Actions | `gh run view --log-failed` |
| test, tests, jest, vitest | project test command (e.g., `pnpm test`, `npm test`, `pytest`) |
| type, typescript | `pnpm check-types` or `tsc --noEmit` |
| lint | `pnpm lint` |
| build, compile | `pnpm build` |
| E2E, UI, browser | Playwright MCP browser tools |
| API, endpoint, REST | WebFetch tool or curl |
| iOS, simulator | `xcodebuild test -scheme <scheme>` |
| CLI binary | direct binary execution + exit-code capture |

**Reproduction-command persistence**: the chosen command is recorded in `reports/root-cause-<slug>.md` so any future re-run uses the same command.

## BEFORE state template

Append to `.progress.md` under `## Reality Check (BEFORE)`:

```markdown
## Reality Check (BEFORE)

**Goal type**: Fix
**Reproduction command**: <verbatim command>
**Failure observed**: Yes / No
**Output (verbatim)**:
```
<paste failure output here, full or first 50 lines>
```
**Timestamp**: <ISO-8601>
**Captured-by**: root-cause-tracing
```

## AFTER state template (filled by VF task)

```markdown
## Reality Check (AFTER)

**Command**: <same reproduction command>
**Result**: PASS / FAIL
**Output (verbatim)**:
```
<paste current output>
```
**Comparison**: BEFORE <X>, AFTER <Y>
**Verified**: Issue resolved / Issue persists
**Timestamp**: <ISO-8601>
```

## VF task format (injected into the plan)

The VF task is added as a late task in any fix-type plan produced after this analysis (typically as `phase-NN/4.3` or the final pre-merge task):

```markdown
- [ ] VF: Verify original issue resolved
  - **Do**:
    1. Read BEFORE state from `.progress.md`.
    2. Re-run reproduction command: `<command>` (from `reports/root-cause-<slug>.md`).
    3. Compare output with BEFORE state.
    4. Document AFTER state in `.progress.md`.
  - **Verify**: `grep -q "Verified: Issue resolved" .progress.md`
  - **Done when**: AFTER shows issue resolved, documented in `.progress.md`.
  - **Commit**: `chore(<name>): verify fix resolves original issue`
```

## Instrument-before-theorize rule

If you can't determine root cause in **10 minutes** of reading code, add instrumentation:
- Print statements at boundary points
- Trace logs at each candidate root cause site
- Live reproduction with the actual data
- THEN re-apply five-whys with empirical evidence

The 10-minute heuristic prevents armchair theorizing.

## Mock-quality red flags (for test-related root causes)

If the failure under analysis is a test failure, run these red-flag checks before declaring root cause. A test that **only validates mocks** is itself a root cause class.

| Red flag | Detection |
|---|---|
| Mock declarations > 3× real assertions | grep `vi.mock\|jest.mock\|mocker.patch` count vs `expect(.*).to\|assert ` count |
| Missing import of the actual module under test | grep for the production import path; if absent, the test isn't testing the production code |
| All assertions are `toHaveBeenCalled` / mock interaction checks | no `toEqual`, `toBe`, `toMatchObject` on real outputs |
| No integration tests in this surface | grep for `integration`, `e2e`, real HTTP/DB calls |
| Missing mock cleanup | no `afterEach(() => { vi.restoreAllMocks() })` or equivalent |

If 3+ red flags trigger, the root cause is "test exists but exercises mocks not production code." Recommended fix: rewrite test to exercise the real path; mock only the I/O boundary.

## Output artifact

`reports/root-cause-<slug>.md` structure:

```markdown
# Root Cause Analysis: <symptom slug>

## Symptom
<one paragraph>

## Reality Check (BEFORE)
<embedded verbatim>

## Five-Whys Cascade
1. Why <symptom>? → <answer + evidence file:line>
2. Why <answer 1>? → <answer + evidence>
3. Why <answer 2>? → <answer + evidence>
4. Why <answer 3>? → <answer + evidence>
5. Why <answer 4>? → <actionable root cause + evidence>

## Fishbone (Ishikawa)
- Code: <any contributing factors>
- Data: <…>
- Config: <…>
- Environment: <…>
- Dependency: <…>
- Human: <…>

## Primary category
<one of the six>

## Recommended Fix
<minimal change + rationale>

## Reproduction Command (persisted)
<verbatim command>

## VF Task (to inject in downstream plan)
<VF task block, copy-paste-ready>

## Mock-Quality Red Flags (if applicable)
<list of triggered flags, or "n/a">
```

## When to use

- `/shannon:why` invocation.
- Phase 2 of `/shannon:fix` (debug step).
- Post-incident analysis.

## When NOT to use

- Obvious bugs (null pointer, typo) — fix and move on.
- Configuration errors with clear error messages — read and fix.

## Iron rules

- **Empirical > theoretical.** Instrument > reason.
- **Five-whys reaches an actionable cause**, not a vague label.
- **Cited evidence per "why" answer** (log path, file:line, command output).
- **BEFORE state captured before any fix attempt.** No retrospective reconstruction.
- **VF task injected into the plan**, not left to the executor's imagination.
- **Mock-only tests counted as a root cause class** when applicable.

## Without / With

| Without root-cause-tracing | With root-cause-tracing |
|---|---|
| "Fix CI" completes but CI still red | CI verified green via VF task before merge |
| Tests "fixed" but original failure unknown | BEFORE/AFTER comparison proves fix |
| Silent regressions | Explicit failure reproduction artifact |
| Manual verification required | Automated VF task in plan |
| Tests pass but only exercise mocks | Mock-quality red flags surface this as a separate root cause |

## Cross-references

- `trace` — backward-causality variant for runtime tracing.
- `skills/no-fakes-discipline/SKILL.md` — mock-detection iron rule authority.
- `skills/plan-author/SKILL.md` — receives the VF task injection.
- `skills/reflect/SKILL.md` — uses root-cause-tracing on a session's gaps.
