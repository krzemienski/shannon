---
name: validate
description: "Detect platform; run validation journeys against real system; capture evidence; emit cited PASS/FAIL verdicts."
argument-hint: "[--mode quick|standard|consensus] [--platform ios|web|api|cli|fullstack]"
---

# /shannon:validate

End-to-end functional validation. Real system in → cited PASS/FAIL verdict out.

## Inputs

- `--mode quick|standard|consensus` (default `standard`)
  - `quick` — critical journeys only
  - `standard` — full discovery + journey execution
  - `consensus` — engages `Skill: consensus-engine` with N=3 independent validators
- `--platform ios|web|api|cli|fullstack` — override autodetect

## Behavior

1. Platform detection: read project markers (Xcode files, `package.json`, `manage.py`, `Cargo.toml`, OpenAPI specs). Override with `--platform`.
2. Invoke `Skill: plan-author` (validation-gate mode) — output: `e2e-evidence/<run-id>/validation-plan.md` listing journeys with PASS criteria per step.
3. Dispatch `Task: validator` (single mode) or `Task: team-validator` (consensus mode).
4. Per journey: capture evidence to `e2e-evidence/<run-id>/<journey-slug>/step-NN-<action>-<result>.<ext>`. Every evidence file must be non-empty.
5. `Skill: evidence-gate` per journey — refuses missing/empty evidence.
6. After all journeys: validator writes per-journey verdict; lead writes `e2e-evidence/<run-id>/report.md`.
7. `--mode consensus`: `Task: team-validator` spawns 3 isolated `Task: validator` instances; `Skill: consensus-engine` synthesizes confidence-scored verdict.

## Skills + agents

- `Task: validator` (single mode)
- `Task: team-validator` (consensus mode)
- `Skill: functional-validation`
- `Skill: evidence-gate`
- `Skill: evidence-indexing`
- `Skill: refusal-discipline`
- `Skill: consensus-engine` (consensus mode only)
- `Skill: no-fakes-discipline` (Iron Rule)
- `Skill: plan-author` (validation-plan generation)

## Iron rules

- No INCONCLUSIVE outcomes — missing evidence = FAIL.
- Every journey has a PASS or FAIL with cited evidence files.
- Evidence inventory file lists every artifact with byte count.

## Examples

```
/shannon:validate
/shannon:validate --mode consensus
/shannon:validate --platform ios --mode standard
```
