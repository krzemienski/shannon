---
name: completion-gate
description: Final completion gate evaluator for Shannon runs. ALWAYS use when the user says "completion gate", "ship gate", "evaluate completion", "final gate", or is about to claim a task is done. Reads the entire evidence tree, checks every Mandatory Success Criterion (MSC) against cited evidence, requires three-reviewer consensus PASS plus Oracle quorum APPROVED, and emits report.json. No override flag, no force-complete. Outer mechanical layer above evidence-gate (per-claim) and verification-before-completion (per-commit).
triggers:
  - "completion gate"
  - "ship gate"
  - "evaluate completion"
  - "final completion gate"
required_hooks:
  - evidence-gate
  - post-action-discipline
---

# completion-gate

Final-gate evaluator. Reads the entire evidence tree, evaluates every Mandatory Success Criterion against cited evidence, requires three-reviewer consensus PASS plus Oracle quorum APPROVED.

## Behavior contract

1. Read `e2e-evidence/<run-id>/` tree.
2. For each MSC (Mandatory Success Criterion) declared in the plan:
   - Locate cited evidence file(s).
   - Verify file exists, non-empty, content supports the claim.
   - Mark MSC: PASS / FAIL / MISSING.
3. Read consensus report (if applicable) — require ≥2/3 reviewer PASS.
4. Read oracle quorum report — require ≥2/3 oracle APPROVE + 0 unresolved critical blockers.
5. Emit `e2e-evidence/<run-id>/completion-gate/report.json`:
   ```json
   {
     "run_id": "...",
     "msc_count": N,
     "msc_pass": M,
     "msc_fail_or_missing": K,
     "reviewer_consensus": "PASS" | "FAIL" | "N/A",
     "oracle_quorum": "APPROVED" | "REFUSED" | "N/A",
     "verdict": "COMPLETE" | "REFUSED",
     "cited_blockers": [ { "msc": "...", "reason": "...", "evidence_path": "..." } ]
   }
   ```
6. If any MSC FAILED, MISSING, or quorum REFUSED → verdict REFUSED. Write `REFUSAL.md` alongside report.json (via `refusal-discipline` skill).

## Verification Requirements by Claim Type

Borrowed from `verification-before-completion`, applied per-MSC inside the gate:

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | N/A — Shannon has no tests; substitute "feature exercised end-to-end with 0 FAILs" | "should pass", agent report |
| Build succeeds | Build command captured in evidence: exit 0 | Linter passing |
| Bug fixed | Original symptom replayed: PASS evidence captured | Code changed, assumed fixed |
| Agent completed | Evidence files exist + content matches MSC | Agent reports "success" |
| Requirements met | Line-by-line MSC checklist with citation per row | Build green |
| Feature works | Real-system exercise + screenshot/curl/CLI evidence READ | File existence |
| Integration verified | Cross-layer evidence (frontend screenshot + backend curl response showing same value) | Single-layer evidence |

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should be COMPLETE now" | Run the gate. Read the report. |
| "I'm confident the MSCs pass" | Confidence is not evidence. Cite files. |
| "The validator agent said PASS" | Validator reports LOCATIONS. The gate verifies CONTENT. |
| "Partial MSC coverage is enough for this iteration" | No. Partial = REFUSED. Iterate again. |
| "Override the quorum, the human will review" | No override flag exists. No `--force-complete`. No `--accept-blockers`. |

## When to use

- the final completion gate in `/shannon:cook`
- Final gate of `/shannon:autopilot` retry loop
- Audit checkpoint via `/shannon:audit-completion`

## When NOT to use

- Mid-iteration (gate only fires at outer boundary)
- Exploratory work without declared MSCs

## Relationship to evidence-gate and verification-before-completion

Shannon uses a **three-layer gate model** — each layer catches what the others miss:

| Layer | Skill | Trigger | Scope |
|-------|-------|---------|-------|
| **Outer mechanical** | `completion-gate` (this skill) | Phase 10 of forge / autopilot final gate / `/shannon:audit-completion` | Whole run; every MSC; consensus + oracle quorum |
| **Per-claim refusal** | `evidence-gate` | About to set TaskUpdate `completed`, before PR creation, before "done" claim | Single claim; 5-question binary checklist (READ / VIEW / EXAMINE / CITE / Skeptic-agree) |
| **Per-commit lightweight** | `verification-before-completion` | About to commit / push / open PR | Single change; "have I run the verification command in this message?" |

Why all three? Because they protect against different failure modes:

- `completion-gate` catches: missing MSCs, fabricated evidence at scale, agent-report-without-content-check, premature run termination.
- `evidence-gate` catches: a single claim flagged "complete" without a cited screenshot, without a viewed image, without examined CLI output.
- `verification-before-completion` catches: "should work" rationalizations, committing-before-running, trusting agent reports for routine in-session work.

The three layers compose. If `verification-before-completion` is honored on every commit, fewer claims reach `evidence-gate` as half-done. If `evidence-gate` refuses honestly, `completion-gate`'s consensus + oracle has cleaner inputs and fails less often. Skipping the lower layers does NOT excuse the upper.

## Iron rules

- **NO override flag.** No `--force-complete`. No `--accept-blockers`. No environment variable that bypasses the gate.
- **NO inferred MSCs** — only those declared in the plan count.
- **Missing evidence = FAIL, not INCONCLUSIVE.**
- **Self-review forbidden** — gate is mechanical, not advisory. The gate does not "weigh in" on tradeoffs.
- **Sub-agent evidence: locations only.** The gate verifies CONTENT of every cited artifact itself. A sub-agent saying "passed" is not a pass.

## Worked Example — sample report.json + REFUSAL.md

**Scenario:** `/shannon:cook` Phase 10 on run `2026-05-27-login-redesign`. 4 MSCs declared. 3 PASS with evidence, 1 MISSING (login error-handling screenshot never captured), oracle quorum APPROVED but one reviewer in consensus voted FAIL on accessibility.

`e2e-evidence/2026-05-27-login-redesign/completion-gate/report.json`:

```json
{
  "run_id": "2026-05-27-login-redesign",
  "msc_count": 4,
  "msc_pass": 3,
  "msc_fail_or_missing": 1,
  "reviewer_consensus": "PASS",
  "oracle_quorum": "APPROVED",
  "verdict": "REFUSED",
  "cited_blockers": [
    {
      "msc": "Login error states render with field-level red text and aria-live region",
      "reason": "MISSING evidence: declared screenshot e2e-evidence/2026-05-27-login-redesign/login-error/step-04-invalid-email.png does not exist on disk",
      "evidence_path": "e2e-evidence/2026-05-27-login-redesign/login-error/step-04-invalid-email.png"
    }
  ]
}
```

`plans/reports/REFUSAL-2026-05-27-login-redesign.md` (emitted by `refusal-discipline`):

```markdown
# REFUSAL — 2026-05-27-login-redesign
**Date:** 2026-05-27T18:42:11Z
**Phase:** Phase 10 — completion-gate

## Cited Blockers

### Blocker 1
- **MSC:** Login error states render with field-level red text and aria-live region
- **Why refused:** MISSING evidence
- **Evidence expected:** e2e-evidence/2026-05-27-login-redesign/login-error/step-04-invalid-email.png
- **Evidence actual:** missing — directory contains step-01 through step-03 only
- **Remediation:** re-run functional-validation on the login-error journey; capture step-04; re-gate

## What was NOT done
- PR not created (gate REFUSED before merge)
- TaskUpdate(completed) not set

## How to retry
- /shannon:cook "capture login-error step-04-invalid-email screenshot and re-validate"
- Or /shannon:autopilot "complete login-redesign" — refusal-driven retry loop
```

## Related Skills

- `evidence-gate` — per-claim 5-question gate (the layer below)
- `verification-before-completion` — per-commit lightweight check (the layer below that)
- `refusal-discipline` — emits `REFUSAL.md` when the gate refuses
- `evidence-indexing` — ensures every evidence directory is navigable so the gate can mechanically traverse
- `functional-validation` — produces the evidence the gate evaluates
- `consensus-engine` — three-reviewer consensus this gate consumes
- `judge` — oracle quorum this gate consumes


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `transform-validation-prompt`

<objective>
Take any prompt — raw text, existing instruction set, task description, or file path — and transform it so every discrete task has a blocking validation gate. Each gate captures real-system evidence, reviews it against pre-defined PASS criteria, and prevents advancement on FAIL.

The transformed prompt enforces the Iron Rule: if the real system doesn't work, fix the real system. Never create mocks, stubs, test doubles, or test files.
</objective>

<quick_start>
**Before (ungated):**
```
Create a REST API endpoint for user registration. Verify it works.
```

**After (gated):**
```
<mock_detection_protocol>
Creating .test.*, mock libraries, in-memory DBs, TEST_MODE flags → STOP. Fix the REAL system.
</mock_detection_protocol>

<task id="1">
Create POST /api/users/register accepting {email, password}. Hash with bcrypt, insert into users table, return user object without password field.
Files: src/routes/register.ts
</task>

<validation_gate id="VG-1" blocking="true">
Prerequisites: pg_isready returns 0 | npm start & | poll curl -sf localhost:3000/health until 200
Execute: curl -s -X POST localhost:3000/api/users/register -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"Secure123!"}' | tee evidence/vg1-response.json | jq .
Pass criteria: HTTP 201 | non-empty "id" | matching "email" | NO "password" field | duplicate → 409
Review: cat evidence/vg1-response.json | jq -e '.id and .email'
Verdict: PASS → proceed | FAIL → fix endpoint → re-run
Mock guard: IF tempted to mock → STOP → fix real system
</validation_gate>

<gate_manifest>
Total gates: 1 | All BLOCKING | Evidence: evidence/
</gate_manifest>
```

The gate is BLOCKING. Nothing after VG-1 executes until evidence proves PASS.
</quick_start>

<essential_principles>
**Iron Rule:** If the real system doesn't work, fix the real system. No mocks, stubs, test doubles, or test files. No exceptions.

**Evidence over assertion:** "It works" is NOT evidence. Evidence is a screenshot showing specific UI state, a curl response with specific JSON fields, or CLI output with specific strings.

**PASS criteria first:** Define criteria BEFORE writing gates. Good criteria are specific, observable, measurable. Bad criteria: "it works", "no errors", "looks good."

**No advancement on FAIL:** Gates are BLOCKING. Task → Execute → Capture Evidence → Review → PASS → Next Task. On FAIL, fix real system and re-run.

**Mock detection embedded:** Every transformed prompt starts with mock detection preamble that halts execution if mock patterns are detected.
</essential_principles>

<workflow>
Follow these steps to transform any input.

**Step 1: Analyze the input.** Parse to extract: objective, platform (see detection table), discrete tasks, ungated assumptions (where "it works" is assumed without proof), and dependencies (databases, servers, services). Load matching platform patterns from [references/_transform-validation-prompt-gate-patterns.md](references/_transform-validation-prompt-gate-patterns.md).

| Signal | Platform | Evidence Tool |
|--------|----------|---------------|
| `.xcodeproj`, SwiftUI, UIKit | iOS/macOS | `xcrun simctl io booted screenshot` |
| `Cargo.toml`, `go.mod`, binary | CLI | `./binary 2>&1 \| tee output.txt` |
| REST routes, API, curl, HTTP | API | `curl -s \| tee response.json \| jq .` |
| React, Vue, Svelte, Playwright | Web | `page.screenshot()` |
| Frontend + backend together | Full-Stack | Bottom-up: DB → API → Frontend |
| None detected | Generic | Command output + file checks |

**Step 2: Inject mock detection preamble** at TOP of transformed prompt:
```
<mock_detection_protocol>
Before executing any task, check intent:
- Creating .test.*, _test.*, *Tests.*, test_* files → STOP
- Importing mock libraries (nock, sinon, jest.mock, unittest.mock) → STOP
- Creating in-memory databases (SQLite :memory:, H2) → STOP
- Adding TEST_MODE or NODE_ENV=test flags → STOP
- Rendering components in isolation (Testing Library, Storybook) → STOP
Fix the REAL system instead. No exceptions.
</mock_detection_protocol>
```

**Step 3: Define PASS criteria per task** — BEFORE writing gates.

Good criteria (specific, observable, measurable):
- "curl returns JSON with `total` > 0 and `items` array non-empty"
- "Screenshot shows dashboard with 3 widget cards containing data"
- "CLI exits 0 and stdout contains `Processed 150 files in`"

Bad criteria — REJECT and rewrite:
- "It works" → What specifically? What do you SEE?
- "No errors" → Absence of errors ≠ correctness
- "Tests pass" → Which tests? Mocked?

**Step 4: Inject validation gates** after each task:
```
<validation_gate id="VG-{N}" blocking="true">
Prerequisites: [Start dependencies + health check — poll, don't guess timing]
Execute: [Real system interaction — save output to evidence/ files]
Capture: [Commands with tee to evidence/vg{N}-{desc}.{ext}]
Pass criteria: [From Step 3 — specific, measurable, pre-defined]
Review: [READ evidence: Read tool for images, cat for text, jq for JSON]
Verdict: PASS → next task | FAIL → fix real system → re-run from prerequisites
Mock guard: IF tempted to mock → STOP → fix real system → re-run
</validation_gate>
```

**Step 5: Append gate manifest** at END:
```
<gate_manifest>
Total gates: {N}
Sequence: VG-1 → VG-2 → ... → VG-N
All gates: BLOCKING (no advancement on FAIL)
Evidence: evidence/
If ANY gate FAILS: Fix real system → re-run from FAILED gate → do NOT skip
</gate_manifest>
```

**Step 6: Present** the transformed prompt with summary: tasks identified, gates injected, platform detected, mock detection embedded, manifest appended.
</workflow>

<reference_index>
All in `references/`:

- **gate-patterns.md** — Platform-specific validation gate templates for iOS, CLI, API, Web, Full-Stack, and Generic platforms
</reference_index>

<success_criteria>
Transformed prompt is complete when:
- Mock detection preamble at the top
- Every task has at least one validation gate
- Every gate has prerequisites (dependencies started + healthy)
- Every gate has PASS criteria (specific, observable, measurable — defined before execution)
- Every gate captures evidence to files (not ephemeral)
- Every gate reviews evidence (READ it, not just check file exists)
- Every gate has mock_guard
- Gate manifest at the bottom
- No vague criteria ("it works", "looks good", "no errors")
- Platform-appropriate evidence methods used
</success_criteria>
