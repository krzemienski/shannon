---
name: fix
description: "Scout → debug → implement → revalidate. Three-strike cap. Each attempt writes fresh evidence directory with a distinct root-cause hypothesis."
argument-hint: "[bug-description | error-log-path] [--auto]"
---

# /shannon:fix

Bug-fix runner with strict revalidation. Three attempts, three distinct root-cause hypotheses, three fresh evidence directories.

## Inputs

- Positional: bug description OR path to error log
- `--auto` — autonomous mode (no AskUserQuestion checkpoints)

## Behavior

For attempt 1..3:

1. **Scout**: read the bug evidence. Grep codebase for surface area (`Skill: codebase-analysis`).
2. **Debug**: invoke `Skill: root-cause-tracing`. Output: a single root-cause hypothesis with cited file:line evidence.
3. **Implement**: dispatch `Task: shannon:executor` with a minimal fix targeting that root cause only. No drive-by improvements.
4. **Revalidate**: invoke `Skill: functional-validation` against the journey that originally exposed the bug.
5. Evidence per attempt under `e2e-evidence/fix-<run-id>/attempt-<N>/`. Never reuse evidence across attempts.
6. If revalidate PASSes → exit success.
7. If FAIL: document why this hypothesis failed in `failed-approaches.md`. Move to attempt N+1 with a DIFFERENT root-cause hypothesis.
8. If 3 attempts all FAIL → mark UNFIXABLE; emit refusal via `Skill: refusal-discipline` pointing to `failed-approaches.md`.

## Skills + agents

- `Skill: codebase-analysis` (scout)
- `Skill: root-cause-tracing` (debug)
- `Task: shannon:executor` (implement)
- `Skill: functional-validation` (revalidate)
- `Skill: refusal-discipline` (on 3-strike exhaustion)
- `Skill: no-fakes-discipline` (Iron Rule throughout)

## Iron rules

- Three-strike cap is hard. No fourth attempt — refusal is the correct outcome.
- Same hypothesis twice = retry, not new attempt. Hypothesis must change.
- No drive-by edits — every changed line traces directly to the cited root cause.

## Examples

```
/shannon:fix "Login button on /login does nothing in Safari"
/shannon:fix logs/build-failure.txt --auto
```
