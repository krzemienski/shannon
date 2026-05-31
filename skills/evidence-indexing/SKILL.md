---
name: evidence-indexing
description: Maintain README.md (purpose) and INDEX.md (artifact enumeration) in every evidence directory. ALWAYS use when the user says "index evidence", "write evidence index", "evidence INDEX.md", "enumerate artifacts", whenever new artifacts land in e2e-evidence/, or when a directory grows beyond 10 files. Refuses to leave any evidence dir un-indexed at gate completion.
triggers:
  - "index evidence"
  - "write evidence index"
  - "evidence INDEX.md"
  - "enumerate artifacts"
---

# evidence-indexing

Every evidence directory must be navigable. This skill enforces that. Load-bearing for `completion-gate` mechanical traversal — the gate walks the evidence tree by reading INDEX.md, so an un-indexed dir is invisible to the gate.

## Behavior contract

After any phase completes (and after every gate):

1. For each subdirectory under `e2e-evidence/<run-id>/`:
   - If `README.md` missing → generate: 1-paragraph purpose statement explaining what this directory contains.
   - If `INDEX.md` missing → generate: enumerated table of every artifact (path, byte count, what it represents).
2. If directory has > 10 files: split INDEX.md into sections by step/journey/role.
3. Verify every artifact in INDEX.md actually exists on disk (no phantom citations).
4. Verify every artifact on disk appears in INDEX.md (no orphaned files).

## INDEX.md structure

```markdown
# Evidence Index — <phase or journey name>

**Run:** <run-id>
**Phase:** <phase number + name>
**Generated:** <ISO-8601>

## Artifacts

| File | Size | Type | What it shows |
|---|---|---|---|
| step-01-login-loaded.png | 24kb | screenshot | /login renders successfully |
| step-02-submit-pressed.png | 28kb | screenshot | Submit button click registered |
| step-03-dashboard.json | 1.2kb | API response | Dashboard payload after auth |
| ... | ... | ... | ... |
```

## README.md structure

```markdown
# <journey or phase name>

**Run:** <run-id>
**Generated:** <ISO-8601>

One paragraph describing what this directory contains, the MSC(s) it
supports, and the producing skill (functional-validation, ios-validation-runner, etc.).
Links to INDEX.md for the artifact enumeration.
```

## When to use

- After every phase artifact lands in `e2e-evidence/`
- Before invoking any gate (`completion-gate`, `judge`)
- As a periodic maintenance pass
- When a directory grows past 10 files (split INDEX.md into sections)

## When NOT to use

- Directories not under `e2e-evidence/` (`logs/`, `reports/`, `plans/` have their own conventions)

## Iron rules

- **Refuse to leave any evidence dir un-indexed at gate-completion time.**
- **Never invent files.** Every INDEX.md entry must exist on disk.
- **Never delete an evidence file** to "clean up" the index — captured = immutable.
- **Never edit an evidence file** in place — captured = immutable. If an artifact is wrong, capture a new one with a new step number; do not overwrite.

## Anti-Patterns

| Pattern | Why It's Wrong | Do This Instead |
|---------|---------------|-----------------|
| Generate INDEX.md once and never update | New artifacts land between phases; a stale INDEX.md is worse than none — it lies | Regenerate INDEX.md after every phase artifact lands; the gate reads INDEX.md, not the file system |
| List directories in INDEX.md instead of files | The gate verifies CONTENT of specific files; a directory entry hides the per-file shape | Enumerate every artifact individually with size and "what it shows" |
| Skip the "what it shows" column "to save time" | An INDEX with no description is just an `ls`; the description is the human-readable claim the gate verifies | Always write the one-line "what it shows" — it forces YOU to verify content before listing it |
| Delete failing-evidence files "to clean up" before re-running | Captured evidence is the audit trail; deleting it erases history a future debug needs | Captured = immutable; re-capture under a new step number (step-03b, step-03-retry) instead |
| Leave orphan files on disk that aren't in INDEX.md | Phantom artifacts make verification non-deterministic; a future gate may pick them up randomly | Either index the orphan with its real "what it shows", or move it to `e2e-evidence/<run-id>/orphans/` with explanation |
| Single flat INDEX.md for a directory of 50 artifacts | Unscannable; the gate's MSC traversal becomes O(N) per MSC | Split into sections by step/journey/role once the directory exceeds 10 files |

## Worked Example

**Scenario:** `e2e-evidence/run-001/login-journey/` contains 5 artifacts after a clean functional-validation run.

`e2e-evidence/run-001/login-journey/README.md`:

```markdown
# login-journey

**Run:** run-001
**Generated:** 2026-05-27T17:02:14Z

Captures the end-to-end login flow exercised by `functional-validation` against
the dev server on :3000. Supports MSCs:
- "login form renders without console errors"
- "valid credentials transition to dashboard"
- "invalid credentials show field-level error with aria-live"

Producing skill: `functional-validation`. See `INDEX.md` for the artifact
enumeration. Cited from `e2e-evidence/run-001/completion-gate/report.json`.
```

`e2e-evidence/run-001/login-journey/INDEX.md`:

```markdown
# Evidence Index — login-journey

**Run:** run-001
**Phase:** Phase 7 — functional-validation
**Generated:** 2026-05-27T17:02:14Z

## Artifacts

| File | Size | Type | What it shows |
|---|---|---|---|
| step-01-login-loaded.png | 24kb | screenshot | /login renders; email + password fields visible; no console errors |
| step-02-credentials-entered.png | 27kb | screenshot | both fields populated; submit button enabled state |
| step-03-login-success.png | 31kb | screenshot | dashboard route; username badge "alex@example.com" top-right |
| step-04-invalid-email-error.png | 25kb | screenshot | invalid-email error rendered field-level; aria-live region announces |
| step-05-dashboard-api-response.json | 1.2kb | API response | GET /api/me returns {"user":"alex@example.com","sessions":3} matching badge |
```

This is what a passing `completion-gate` traversal expects to find — every MSC has a one-line claim and a specific file. No orphans, no directories, no missing rows.

## Shannon Runtime Integration

- **Mechanical traversal:** `completion-gate` walks `e2e-evidence/<run-id>/` by reading each `INDEX.md`. An un-indexed dir is invisible to the gate; this skill prevents that invisibility.
- **Cited from:** `evidence-gate` Q4 (CITE proof) references specific files this skill enumerates. The "what it shows" column IS the claim being cited.
- **Immutable artifacts:** the rule "captured = immutable" composes with `block-fab-files`. Edits to evidence files are not allowed; re-captures get new step numbers.

## Related Skills

- `completion-gate` — outer gate that traverses the structure this skill maintains
- `evidence-gate` — per-claim gate whose Q4 (CITE proof) names files this skill enumerates
- `functional-validation` — primary producer of the artifacts this skill indexes
- `refusal-discipline` — emits `REFUSAL.md` that cites files this skill enumerates
