---
name: resume
description: "Inspect evidence tree; identify last completed phase; resume from next missing artifact. Evidence-tree-as-state."
argument-hint: "[--run-id <id>]"
---

# /shannon:resume

Resume a halted `/shannon:cook` or `/shannon:autopilot` run. The evidence tree IS the state — no separate state file.

## Inputs

- `--run-id <id>` — run identifier (default: latest under `e2e-evidence/`)

## Behavior

1. Resolve run-id (latest or as provided).
2. Walk `e2e-evidence/<run-id>/` directories in canonical phase order:
   - `codebase-analysis/`
   - `plan/`
   - `pre-execution-review/` (if engaged)
   - `execution/`
   - `validation/`
   - `consensus/` (if consensus mode was used)
   - `post-execution-review/`
   - `completion-gate/`
3. Find first directory missing its `INDEX.md` or expected terminal artifact (e.g., `verdict.md`, `report.json`).
4. Restart pipeline from that phase. Prior phases trusted as complete.

## Skills + agents

- `Skill: session-handoff` (state-from-disk reader)
- `Skill: completion-gate` (state inspection)
- `Skill: evidence-indexing` (per-phase INDEX.md verification)
- Whichever phase agent the resumed phase requires (e.g., `Task: shannon:executor`, `Task: shannon:validator`)

## Iron rules

- Never restart a completed phase on resume — contamination risk.
- Never invent state — the evidence tree is the truth.

## Examples

```
/shannon:resume
/shannon:resume --run-id 260528-1334
```
