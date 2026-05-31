---
name: evidence-gate
description: 6-question refusal-discipline checklist applied before any completion claim. ALWAYS use when the user says "marking complete", "task complete", "ready to ship", "PR ready", "ready for review", "mark as done", "claim completion", or before any TaskUpdate to completed / PR creation / done assertion. Any single "no" answer refuses completion. Verifies CONTENT of sub-agent evidence, not just LOCATION.
triggers:
  - "marking complete"
  - "task complete"
  - "ready to ship"
  - "PR ready"
  - "ready for review"
  - "mark as done"
  - "claim completion"
required_hooks:
  - evidence-gate
  - post-action-discipline
---

# evidence-gate

## What MSC means

**MSC = Minimum Sufficient Criterion**. A specific, citable, gate-criterion line from a plan or task spec. "All MSCs pass" means every MSC has its own cited evidence file; aggregate "looks good" verdicts are refused. Used throughout Shannon's evidence-gate, completion-gate, refusal-discipline workflows.


Refusal-discipline gate. Six questions, all must be YES, or the gate refuses.

This is Shannon's per-claim layer in the three-gate model: outer-mechanical `completion-gate` evaluates the whole run; `evidence-gate` (this skill) evaluates each completion claim individually; `verification-before-completion` is the lightest, applied per-commit.

## Behavior contract

Before any TaskUpdate to `completed`, before any PR creation, before any "done" claim:

1. **READ evidence?** Did you personally read the cited evidence files? Not "an agent says so" — YOU.
2. **VIEW screenshot?** If UI work: did you visually inspect the screenshot? Not just confirm it exists.
3. **EXAMINE output?** If CLI / API work: did you read the actual stdout / response body? Not just exit code.
4. **CITE proof?** Does every claim of PASS cite a specific file path (with line range where relevant)?
5. **Skeptic agree?** Would a skeptical reviewer agree the cited evidence supports the claim?
6. **CONTENT verified, not just LOCATION?** Where a sub-agent or worker provided evidence, did YOU open the artifact and verify its CONTENT — not just that the file exists at the LOCATION the sub-agent reported?

Any answer of NO → REFUSE completion. Write findings, route to `refusal-discipline` skill.

## Why Q6 is non-negotiable

Sub-agents report success based on file existence. A screenshot of a crash dialog is still a `.png` file. A curl response of `{"error": "not found"}` is still a 200-byte JSON file. Workers provide evidence LOCATIONS. YOU verify evidence CONTENT.

Even when spawning parallel workers — workers provide locations, YOU open and read each artifact. Never trust "X passed" without examining X.

## When to use

- About to set TaskUpdate status=completed
- About to write "ready to ship" in a PR
- About to commit with "feat: done" message
- Hook `evidence-gate` fires (PreToolUse:TaskUpdate)
- After a parallel dispatch where multiple workers return "PASS"

## When NOT to use

- Mid-iteration in a loop (use only at the OUTER gate of the iteration, not on every inner step)
- Exploratory work without a completion claim
- Pure planning / drafting phases

## Anti-Patterns

| Pattern | Why It's Wrong | Do This Instead |
|---------|---------------|-----------------|
| "Agent reported 10/10 pass" | Sub-agent reports based on file existence, not content; the screenshot might show a crash dialog | Read the actual artifacts: open every screenshot, cat every text output, verify each matches the MSC |
| "Screenshot was captured" with no content check | A `.png` file proves a screenshot exists, nothing more — the pixels may show an error state | View the screenshot, describe what you SEE in the image, compare to PASS criteria |
| "Build succeeded" with no quoted output | Exit code 0 can hide warnings, skipped steps, or wrong-target builds | Quote the actual success line and timestamp; confirm the target was the one you meant to build |
| "All tasks complete" without per-claim citation | Aggregate verdicts hide per-claim failures | Verify each MSC has its own citation; no aggregate-only PASS |
| "Gate 3 PASS" with no file references | A bare PASS verdict is indistinguishable from confirmation bias | Cite: "screenshot e2e-evidence/.../step-03.png shows badge='41 sessions' matching MSC line 12" |
| "Tests pass" in Shannon | Shannon has no tests; this claim is structurally impossible | Substitute: "feature exercised end-to-end with evidence captured for each MSC" |

## Failure Recovery — If You Already Marked Complete

If you realize you marked something complete prematurely:

1. Immediately acknowledge the error in the next assistant turn
2. Re-open the task / re-set TaskUpdate to `in_progress`
3. Perform proper Q1–Q6 verification
4. Document what evidence was actually missing in `REFUSAL.md`
5. Route to `refusal-discipline` for the next remediation prompt

There is no shame in honest backtrack. There IS a problem with leaving a premature `completed` in place.

## When In Doubt

Ask: "If someone challenged this completion claim, what specific evidence file (with line range, where relevant) would I show them?"

If you cannot answer with specific citations, **the task is NOT complete.**

## Iron rules

- Gate is binary. Yes-to-all-6 OR refuse. No "mostly yes". No "I think so".
- Self-review counts. The skill is the gate — running through 6 questions personally IS the discipline.
- No override flag. Calling this gate and ignoring its refusal is a bug, not a feature.
- Sub-agent assertions are LOCATIONS, not CONTENT. The gate verifies CONTENT directly.

## Example refusal

```
Q1 READ evidence: NO — I never opened step-03-login-success.png
Q2 VIEW screenshot: N/A
Q3 EXAMINE output: PARTIAL — read exit code, didn't read stdout
Q4 CITE proof: NO — claim "feature works" lacks file:line
Q5 Skeptic agree: NO — evidence dir has 2 zero-byte files
Q6 CONTENT verified: NO — only sub-agent reports, no direct file reads

→ REFUSED. Re-run functional-validation, then re-gate.
```

## Shannon Runtime Integration

- **`evidence-gate` hook** — PreToolUse:TaskUpdate triggers a reminder injection ensuring this skill is in-context before any `completed` write.
- **Layering:** runs AFTER `functional-validation` produces evidence, BEFORE `completion-gate` evaluates the whole run, in parallel concern with `verification-before-completion` (which runs per-commit).
- **Refusal output:** routes to `refusal-discipline`, which writes the structured `REFUSAL.md`.

## Related Skills

- `refusal-discipline` — emits `REFUSAL.md` when this gate refuses
- `completion-gate` — outer mechanical gate (whole run; this gate is per-claim)
- `functional-validation` — produces the evidence this gate evaluates
- `verification-before-completion` — lightweight per-commit / per-PR sibling check
- `visual-inspection` — per-screenshot QA used inside Q2
- `evidence-indexing` — keeps evidence directories navigable so this gate can find what it cites


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `verification-before-completion`

# Verification Before Completion

Shannon's lightweight per-commit / per-claim layer in the three-gate model. Sits below `evidence-gate` (per-claim refusal checklist) and `completion-gate` (outer mechanical evaluator). Use this on every commit / push / PR boundary; the others gate at coarser scopes.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status:
1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
5. ONLY THEN: Make the claim
```

## Verification Requirements by Claim Type

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | N/A in Shannon (no tests). Substitute: feature exercised end-to-end with evidence | "should pass", "previous run" |
| Build succeeds | Build command: exit 0 in THIS message | Linter passing, previous build log |
| Bug fixed | Original symptom: replayed and passes now | Code changed, assumed fixed |
| Agent completed | VCS diff shows expected changes; agent's reported files actually exist and contain expected content | Agent reports "success" |
| Requirements met | Line-by-line MSC checklist with citations | Aggregate green |
| Feature works | Real-system exercise + screenshot/curl/CLI evidence READ | File existence, build green |
| Refactor safe | Pre/post functional-validation produces identical evidence on the unchanged surface | "looks fine", "spot-checked one screen" |
| Migration complete | Old path 404s, new path 200s, data shape matches; all three captured this message | Code path replaced in source |

## Red Flags — STOP Immediately

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification
- About to commit/push/PR without verification
- Trusting agent success reports without independent check
- ANY wording implying success without having run verification

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence is not evidence |
| "Linter passed" | Linter is not compiler |
| "Agent said success" | Verify independently |
| "Partial check is enough" | Partial proves nothing |
| "It worked last time I ran it" | "Last time" is not "this message" |
| "I'll verify after the commit" | The commit IS the claim; verify before |

## Anti-Patterns

| Pattern | Why It's Wrong | Do This Instead |
|---------|---------------|-----------------|
| Saying "should work now" after code change | Code changes are not evidence; untested assumptions cause regressions | Run the verification command fresh, read full output, confirm zero failures |
| Trusting agent success reports without independent check | Agents can report success on partial completion or misinterpreted output | Run verification yourself; check exit codes, failure counts, actual output |
| Using linter pass as proof of build success | Linter checks syntax/style, not compilation or runtime correctness | Run the actual build command and confirm exit code 0 |
| Committing/pushing before running verification | Broken code reaches shared branches; CI catches what you should have | Always run full verification suite before any git commit or push |
| Checking only exit code, ignoring output content | Exit code 0 with "3 tests skipped" or warnings can hide real failures | Read full output — count failures, warnings, skipped items explicitly |

## When NOT to Use

- Exploratory coding where completion is not being claimed — just experimenting
- Reading/researching code without making changes — no claim to verify
- When `evidence-gate` is already enforcing per-claim verification at this boundary (don't double-gate the same claim; use the heavier one)
- When `completion-gate` is the active outer boundary — this skill is the lighter sibling

## Conflicts

- `evidence-gate`: Both enforce evidence-before-claims. This skill is the lighter per-commit version; `evidence-gate` is the binary 6-question per-claim version. Use this on every commit, `evidence-gate` at the per-claim boundary (TaskUpdate completed, PR creation).
- `completion-gate`: Both enforce evidence-before-claims. This skill is the lightest, per-commit. `completion-gate` is the heaviest, per-run. Compose all three — they catch different failure modes.
- `functional-validation`: Complementary. functional-validation defines WHAT to validate (real system, real UI); this skill defines WHEN to verify (before any completion claim).

## Shannon Runtime Integration

- **Layering note:** this skill is the LIGHTEST gate in Shannon's three-layer model. `completion-gate` is the outer mechanical layer (whole run, MSC-level, consensus + oracle). `evidence-gate` is the per-claim layer (6 binary questions before any "done" claim). This skill is the per-commit / per-PR layer (have I run the verification in THIS message?).
- **No override flag.** Same iron rule as the heavier gates.
- **Compose, don't substitute:** invoking this skill does NOT excuse invoking `evidence-gate` at the per-claim boundary, nor `completion-gate` at the run boundary.

## Related Skills

- `evidence-gate` — per-claim 6-question gate (the layer above)
- `completion-gate` — outer mechanical gate (the layer above that)
- `functional-validation` — the Iron Rule for real-system validation
- `no-fakes-discipline` — refuses the substitution attempts this skill's "fresh evidence" requirement would otherwise route around
- `refusal-discipline` — emits `REFUSAL.md` when refusal cascades up from this skill's failures
- `e2e-validate` — platform-routed engine producing the evidence this skill verifies

## Absorbed from `reality-verification`

# Reality Verification

For fix goals: reproduce the failure BEFORE work, verify resolution AFTER.

## Goal Detection

Classify user goals to determine if diagnosis is needed. See `references/_reality-verification-goal-detection-patterns.md` for detailed patterns.

**Quick reference:**
- Fix indicators: fix, repair, resolve, debug, patch, broken, failing, error, bug
- Add indicators: add, create, build, implement, new
- Conflict resolution: If both present, treat as Fix

## Command Mapping

| Goal Keywords | Reproduction Command |
|---------------|---------------------|
| CI, pipeline | `gh run view --log-failed` |
| test, tests | project test command |
| type, typescript | `pnpm check-types` or `tsc --noEmit` |
| lint | `pnpm lint` |
| build | `pnpm build` |
| E2E, UI | Playwright MCP browser tools |
| API, endpoint | WebFetch tool |

For E2E/deployment verification, use MCP tools (Playwright MCP browser tools for UI, WebFetch tool for APIs).

## BEFORE/AFTER Documentation

### BEFORE State (Diagnosis)

Document in `.progress.md` under `## Reality Check (BEFORE)`:

```markdown
## Reality Check (BEFORE)

**Goal type**: Fix
**Reproduction command**: `pnpm test`
**Failure observed**: Yes
**Output**:
```
FAIL src/auth.test.ts
  Expected: 200
  Received: 401
```
**Timestamp**: 2026-01-16T10:30:00Z
```

### AFTER State (Verification)

Document in `.progress.md` under `## Reality Check (AFTER)`:

```markdown
## Reality Check (AFTER)

**Command**: `pnpm test`
**Result**: PASS
**Output**:
```
PASS src/auth.test.ts
All tests passed
```
**Comparison**: BEFORE failed with 401, AFTER passes
**Verified**: Issue resolved
```

## VF Task Format

Add as task 4.3 (after PR creation) for fix-type specs:

```markdown
- [ ] 4.3 VF: Verify original issue resolved
  - **Do**:
    1. Read BEFORE state from .progress.md
    2. Re-run reproduction command: `<command>`
    3. Compare output with BEFORE state
    4. Document AFTER state in .progress.md
  - **Verify**: `grep -q "Verified: Issue resolved" ./specs/<name>/.progress.md`
  - **Done when**: AFTER shows issue resolved, documented in .progress.md
  - **Commit**: `chore(<name>): verify fix resolves original issue`
```

## Test Quality Checks

When verifying test-related fixes, check for mock-only test anti-patterns. See `references/_reality-verification-mock-quality-checks.md` for detailed patterns.

**Quick reference red flags:**
- Mock declarations > 3x real assertions
- Missing import of actual module under test
- All assertions are mock interaction checks (toHaveBeenCalled)
- No integration tests
- Missing mock cleanup (afterEach)

## Why This Matters

| Without | With |
|---------|------|
| "Fix CI" spec completes but CI still red | CI verified green before merge |
| Tests "fixed" but original failure unknown | Before/after comparison proves fix |
| Silent regressions | Explicit failure reproduction |
| Manual verification required | Automated verification in workflow |
| Tests pass but only test mocks | Tests verify real behavior, not mock behavior |
| False sense of security from green tests | Confidence that tests catch real bugs |

## Absorbed from `gate-validation-discipline`

# Gate Validation Discipline

In Shannon, this discipline is owned by `evidence-gate` (per-claim 6-question
binary checklist) and `completion-gate` (outer mechanical run-level evaluator).
This file exists as a discoverability pointer so that anyone reaching for the
upstream-named skill lands in the right place — and as a self-contained
fallback when neither Shannon gate is loaded.

**For Shannon runs, prefer the Shannon-native gates:**

- **`evidence-gate`** — per-claim 6-question gate. Use before any single
  "done" claim (TaskUpdate completed / PR creation / "ready to ship").
- **`completion-gate`** — outer mechanical gate. Use at Phase 10 of
  `/shannon:cook`, at the final gate of `/shannon:autopilot`, or at
  `/shannon:audit-completion`.
- **`verification-before-completion`** — lightweight per-commit / per-PR
  check that sits below both.

The discipline below is the upstream framing, preserved verbatim so the patterns
are usable even when the Shannon gates aren't installed.

## The Verification Loop

When a sub-agent or worker completes work:

```
1. Sub-agent completes work
2. Sub-agent provides evidence LOCATION
3. YOU personally examine evidence CONTENT
4. YOU match evidence to validation criteria
5. YOU cite specific proof (file paths, line numbers, exact output)
6. ONLY THEN mark complete
```

Even when spawning parallel workers — workers provide evidence LOCATIONS, YOU verify evidence CONTENT. Never trust "X passed" without examining X.

## Anti-Patterns

| Bad Pattern | Correct Approach |
|-------------|------------------|
| "Agent reported 10/10 pass" | Read the actual test outputs |
| "Screenshot was captured" | View screenshot, describe what you SEE |
| "Build succeeded" | Quote the actual success output line |
| "All tasks complete" | Verify each criterion has evidence |
| "Gate 3 PASS" (no citations) | Cite: "Screenshot X shows Y at line Z" |

## Failure Recovery

If you realize you marked something complete prematurely:
1. Immediately acknowledge the error
2. Re-open the task/gate
3. Perform proper verification
4. Document what evidence was actually missing

## When In Doubt

Ask: "If someone challenged this completion claim, what specific evidence would I show them?"

If you can't answer with specific citations, **the task is NOT complete**.

## When NOT to Use

- Purely exploratory research or codebase scouting (no completion claim being made)
- Planning phases where no deliverable is being marked complete
- Code reading or analysis without a validation gate
- When the task explicitly says "draft" or "work in progress" (no completion claim)
- **When `evidence-gate` or `completion-gate` is the more specific Shannon gate for the boundary** — prefer those.

## Conflicts

- `evidence-gate` — Shannon's per-claim implementation of this discipline as a binary 6-question checklist. Shannon's v7 Conflict 4 resolution merges this discipline INTO `evidence-gate`. Use `evidence-gate` as the authoritative per-claim Shannon gate; this skill is a discoverability pointer + standalone fallback.
- `completion-gate` — Shannon's outer mechanical implementation of this discipline at run level. Use `completion-gate` at the final completion gate in `/shannon:cook`.
- `verification-before-completion` — lightweight per-commit version. Use for routine pre-commit / pre-PR claims.
- `functional-validation` — Complementary: functional-validation defines WHAT to validate and HOW. Gate-validation-discipline defines WHEN (at every gate) and the evidence-citation standard. Use both together.

## Related Skills

- `evidence-gate` — Shannon-native per-claim gate (PREFERRED)
- `completion-gate` — Shannon-native outer mechanical gate (PREFERRED)
- `verification-before-completion` — lightweight per-commit sibling
- `functional-validation` — the Iron Rule and platform-specific validation protocols
- `e2e-validate` — execution engine that produces the evidence this skill verifies
- `no-fakes-discipline` — prevents circumventing gates with substitutions (Shannon-merged form of `no-mocking-validation-gates`)
- `full-functional-audit` — systematic audit that uses this discipline at every gate
- `plan-author` — plans with embedded gates that require this discipline
