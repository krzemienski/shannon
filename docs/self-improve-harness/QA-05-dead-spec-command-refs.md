# QA-05 — Dead `/shannon:spec` command references

## Finding (P1)

`commands/spec.md` does **not** exist in the v7 tree — the greenfield wipe that
consolidated Shannon down to 29 commands never re-ported it. Yet 15 live,
user-facing references still pointed users at `/shannon:spec`. Because no command
backs that name, every one of those invocations was a **silent no-op** for users:
the model sees an undefined slash command and nothing runs.

Real, existing commands for the same intent:
- `/shannon:prd` — interview-driven PRD authoring (`commands/prd.md`), feeds `/shannon:plan`.
- `/shannon:plan` — hierarchical phased planning with validation gates (`commands/plan.md`).

The `spec-workflow` skill was additionally broken: its entire premise was the
dead `ralph-specum` namespace. It advertised `/shannon:spec` AND a table of dead
`/ralph-specum:*` phase subcommands (`research`/`requirements`/`design`/`tasks`/
`implement`/`triage`/`status`/`switch`/`cancel`/`refactor`) — none of which exist
as commands in v7.

## Decision

Repoint live user-facing refs to the correct real command rather than recreating
`commands/spec.md` (recreating it would fight v7's deliberate 29-command
consolidation). PRD-authoring contexts → `/shannon:prd`. The `spec-workflow`
skill was de-dead-namespaced: rewritten to describe the real
`prd → plan → cook → validate` flow.

Left untouched (session history, not user onboarding): `docs/`, `.v7/`,
`.prompts/`, `v1/`, `archive/`.

## Files changed

| File | Change |
|------|--------|
| `CLAUDE.md` (:46, :112, :120) | Quick-start example + SDK example prompt + namespaced-command note → `/shannon:prd` |
| `skills/autopilot-runner/SKILL.md` (:40, :163) | Phase-1 Spec command `/shannon:spec` → `/shannon:prd`; artifact path `spec/spec.md` → `prd/PRD.md` |
| `skills/interview-framework/references/algorithm.md` (:9) | `/shannon:spec — before generating the spec` → `/shannon:prd — before generating the PRD` |
| `skills/python-agent-sdk/SKILL.md` (:91, :109) | Namespaced-command list + SDK query example → `/shannon:prd` |
| `skills/spec-workflow/SKILL.md` | Full rewrite — dropped every `/shannon:spec` and `/ralph-specum:*` token; now documents the real `prd → plan → cook → validate` flow (kept `triggers` frontmatter for activation) |

## Before / after

- `/shannon:spec` refs in `CLAUDE.md` + `skills/` (excluding archive):
  - **Before:** 38 matches across 5 files (3 CLAUDE.md, 2 autopilot-runner, 1 interview-framework algorithm, 2 python-agent-sdk, 30 spec-workflow)
  - **After:** 0
- `spec-workflow` dead tokens (`/shannon:spec` or `/ralph-specum:`):
  - **Before:** present (30 matches)
  - **After:** NONE (clean)
- Regression: `python3 tests/validate_skills.py` → exit `0` (✅ All skills valid)

Evidence: `.v7/runs/phase-6-qa-selfimprove/iter-1/QA-05-before.log`,
`.v7/runs/phase-6-qa-selfimprove/iter-1/QA-05-after.log`.

Commit: see `git log` for `qa(docs): repoint dead /shannon:spec refs to real commands [QA-05]`.
