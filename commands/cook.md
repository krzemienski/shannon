---
name: cook
description: "Execute a plan or brief end-to-end with iron-rule validation + evidence gates. Wraps planning, execution, validation, completion gate."
argument-hint: "[plan-path | task-description] [--auto] [--fast] [--no-validate] [--greenfield]"
---

# /shannon:cook

End-to-end implementation runner. Plan if needed → execute against real system → validate functionally → gate on evidence before done.

## Inputs

- Positional: plan path OR free-form task description
- `--auto` — small-task path: skip planner, dispatch executor directly
- `--fast` — skip non-critical refinement loops
- `--no-validate` — skip post-execution validation (NOT recommended; documented escape)
- `--greenfield` — opt out of the codebase-analysis pre-flight (use ONLY for empty/new repos). By default cook always runs `/shannon:scope` first on non-empty codebases per the MANDATORY CODE BASE ANALYSIS rule.

## Behavior

1. **Pre-flight (default; non-skippable on non-empty repos):** auto-invoke `/shannon:scope --task "<positional arg>"` to run codebase-analysis + skill-inventory + observability-report in parallel. Skip ONLY if `--greenfield` is passed. The scope-report becomes the planner's context.
2. Argument classification: if arg resolves to filesystem path → read as plan; else treat as brief.
3. If brief AND not `--auto`: invoke `Task: shannon:planner` with the scope-report as context → emits `plans/<date>-<slug>/{plan.md, phase-NN-*.md}`. Every plan task cites a specific file or a specific skill from the scope-report.
4. If brief AND `--auto`: skip planner; synthesize a one-shot phase prompt inline.
5. Spawn `Task: shannon:executor` with phase plan + IRON-RULE injection.
6. After executor completes each phase: invoke `Skill: functional-validation` against the affected surface (unless `--no-validate`).
7. Before marking complete: invoke `Skill: evidence-gate` — 5-question checklist must all answer yes.
8. Before marking complete: invoke `Skill: completion-gate` — mechanical criteria check.
9. On any FAIL: route to `/shannon:fix` flow OR surface refusal via `Skill: refusal-discipline`.

## Skills + agents

- `Task: shannon:planner` (unless `--auto` or path arg)
- `Task: shannon:executor` (always)
- `Task: shannon:team-qa` (per-phase QA cycle — build/lint/test loops with stall detection)
- `Skill: plan-author` (planner's embedded skill)
- `Skill: functional-validation`
- `Skill: evidence-gate`
- `Skill: completion-gate`
- `Skill: no-fakes-discipline` (Iron Rule enforcement)
- `Skill: refusal-discipline` (on gate refusal)

## Success criteria

- All phases executed; evidence under `e2e-evidence/<run-id>/`
- `evidence-gate` PASS + `completion-gate` PASS
- No FAIL verdicts open at exit

## Examples

```
/shannon:cook plans/260528-1334-feature-x/
/shannon:cook "Add OAuth login to settings screen"
/shannon:cook "Bump prisma to 6.4" --auto
```
