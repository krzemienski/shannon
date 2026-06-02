---
name: audit
description: "Read-only audit with severity classification. Scopes: screen, app, session, drift. No edits."
argument-hint: "--scope screen|app|session|drift|completion-evidence [--days N] [--run-id <id>]"
---

# /shannon:audit

Read-only audit. Severity-classified findings. Never edits source.

> v1 consolidation: absorbs the legacy `/shannon:audit-completion` command under `--scope completion-evidence`.

## Inputs

- `--scope screen|app|session|drift|completion-evidence` (required)
  - `screen` — single UI screen visual + interaction audit
  - `app` — full app audit (every screen, every endpoint)
  - `session` — retrospective on session JSONL data
  - `drift` — compare plan claims vs actual codebase state over N days
  - `completion-evidence` — read evidence tree for a completion run, print verdict table
- `--days N` — drift window (default 7)
- `--run-id <id>` — completion-evidence target (default: latest under `e2e-evidence/`)

## Behavior

### scope=screen
- Invoke `Skill: visual-inspection` on the screenshot under audit.
- Output: `reports/audit-screen-<slug>.md` with BLOCKING/HIGH/MEDIUM/LOW findings.

### scope=app
- Invoke `Skill: full-functional-audit` (walks every route/view + interaction inventory).
- Output: `reports/audit-app-<run-id>.md`.

### scope=session
- Invoke `Skill: observability-report` against recent session JSONLs.
- Output: `reports/audit-session-<run-id>.md`.

### scope=drift
- Read `plans/` for the past `--days` days.
- For each plan: search session evidence for the work; grep codebase for claims.
- Classify: VERIFIED / DRIFT / SUPERSEDED.
- Output: `reports/audit-drift-<window>-days.md`.

### scope=completion-evidence
- Resolve run-id (latest or as provided).
- Read `e2e-evidence/<run-id>/completion-gate/report.json` for verdict table.
- Read `e2e-evidence/<run-id>/consensus/report.md` (if exists).
- Spawn `Task(subagent_type=shannon:critic)` to verify each cited evidence file.
- Output: stdout summary + `reports/completion-<run-id>.md`.

## Skills + agents

- `Skill: visual-inspection` (screen/app)
- `Skill: full-functional-audit` (app)
- `Skill: observability-report` (session)
- `Skill: completion-gate` (completion-evidence)
- `Skill: evidence-indexing` (completion-evidence)
- `Task: shannon:critic` (completion-evidence severity audit)

## Success criteria

- Every finding cites a specific file path or screenshot artifact.
- Severity assigned to every finding.
- No code edits (verified by `git diff` empty at exit).

## Examples

```
/shannon:audit --scope screen
/shannon:audit --scope app
/shannon:audit --scope drift --days 14
/shannon:audit --scope completion-evidence --run-id 260528-1334
```
