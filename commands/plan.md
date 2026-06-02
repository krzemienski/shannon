---
name: plan
description: "Plan author. ALWAYS runs codebase-analysis + skill-inventory first if a codebase is present (no opt-in needed). Then applies the planning mode: linear | converge | tournament | deep. Use --greenfield to skip the analysis pre-step for new projects."
argument-hint: "<feature-or-task-description> [--mode linear|converge|tournament|deep] [--greenfield] [--phases N] [--candidates N] [--rounds N]"
---

# /shannon:plan

Plan authoring with mode-based depth control.

> v1 consolidation: absorbs legacy `/shannon:plan-author` (`--mode converge`), `/shannon:plan-author` (`--mode tournament`), `/shannon:plan-deep` (`--mode deep`).

## Inputs

- Positional: feature description or task brief
- `--mode linear|converge|tournament|deep` (default `linear`) — planning strategy, applied AFTER the scope pre-flight in Step 0
- `--phases N` — target phase count for `linear` (default: auto)
- `--candidates N` — candidate count for `tournament`/`deep` (default 3)
- `--rounds N` — round count for `converge`/`deep` (default 3)
- `--greenfield` — opt out of codebase-analysis pre-flight (use ONLY for empty repos)

## Behavior

### Step 0 — Codebase + skill pre-flight (default; non-skippable on non-empty repos)

EVERY `/shannon:plan` run starts with this step. It is not optional.

1. **Detect codebase.** Check for `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, or any non-empty `src/`, `lib/`, `app/`. If found, the project is brownfield and Step 0a + Step 0b run.
2. **Step 0a — `/shannon:scope` (auto-invoked).** Three parallel streams via `Task: shannon:team-builder`:
   - `Skill: codebase-analysis` (5 parallel scientists: inventory + deps + entry-points + proving-cmds + module-map)
   - `Skill: skill-inventory` (enumerates installed skills + uninstalled candidates; maps to task)
   - `Skill: observability-report` (recent session decisions/lessons)
3. **Step 0b — Plan grounded in scope-report.** `Task: shannon:planner` receives the scope-report alongside the brief; every plan task cites either a specific file/module (from codebase-analysis) or a specific skill (from skill-inventory) — never "use a planning skill" generically.

### `--greenfield` opt-out (rare)

If the project is genuinely new (no `.git/`, no source dirs, empty repo), Step 0a is skipped. `skill-inventory` STILL runs (because skill availability is task-relevant even on greenfield projects). `codebase-analysis` is omitted because there's no code yet.

Per the user's CLAUDE.md MANDATORY CODE BASE ANALYSIS rule: analysis is the floor, not a feature. The flag exists only so greenfield work isn't blocked waiting for code that doesn't exist.

### Step 1 — Apply the planning mode

After Step 0, the planner produces the plan using the selected `--mode`:

### mode=linear (default)
Fast hierarchical plan.

1. Invoke `Skill: plan-author` against the brief.
2. Output: `plans/<date>-<slug>/plan.md` (overview, <80 lines) + `phase-01-...md`, `phase-02-...md`, etc.
3. Per phase: Context links, Overview, Requirements, Architecture, Related files, Implementation steps, Todo list, Success criteria, Risk, Security, Next steps.
4. Final phase always validation (unless no user-facing change).

### mode=converge
Iterative refine → critique → revise.

1. Round 1: `Task: shannon:planner` produces draft.
2. `Task: shannon:critic` reviews; emits findings BLOCKING/HIGH/MEDIUM/LOW.
3. Round 2: `Task: shannon:planner` re-runs with critique as input.
4. Convergence: ≤1 BLOCKING from critic → CONVERGED; promote.
5. Each round writes `plans/converge-<run-id>/round-<N>/{draft.md, critique.md}`.

### mode=tournament
N parallel candidates with distinct perspectives.

1. Spawn N `Task: shannon:planner` in parallel via single-message multi-Task pattern. Distinct perspectives per candidate (security-first, performance-first, simplicity-first, etc.).
2. Each candidate writes complete plan to `plans/tournament-<run-id>/candidate-<N>/`.
3. Per candidate: spawn `Task: shannon:critic` — emits findings.
4. `Skill: judge` aggregates scores; winner selected.
5. Loser plans archived under `_rejected/` (never deleted).

### mode=deep
Full deepest-plan treatment, authored by the `deepplan-architect` agent.

1. Dispatch `Task: shannon:deepplan-architect` (inherits codebase-analysis + skill-inventory + plan-author + wave-execution).
2. Run `--mode tournament`.
3. Feed tournament winner into `--mode converge` (2-3 rounds).
4. Invoke `Skill: plan-author` in validation-gate mode: for each phase add explicit validation gates (PASS criteria + required evidence type).
5. **Wave decomposition** — invoke `Skill: wave-execution` to partition the final phase plan into dependency-ordered waves (each wave = tasks whose `blockedBy` is satisfied), so `/shannon:cook` / `executor` can spawn each wave's agents in one message for true parallelism.
6. Synthesize final plan + wave map; archive intermediate rounds under `_history/`.

## Skills + agents

- `Skill: plan-author` (canonical — absorbs converge/tournament/create-plans/plan-author)
- `Skill: interview-framework` (intake)
- `Skill: goal-condition-architect`
- `Skill: spec-workflow`
- `Skill: create-meta-prompts`
- `Skill: gepetto` (`--mode deep` — multi-LLM external plan review for the deepest treatment)
- `Task: shannon:planner` (orchestrator)
- `Task: shannon:critic` (red-team review in converge/tournament/deep)
- `Skill: judge` (tournament/deep ranking)
- `Skill: consensus-engine` (deep synthesis)

## Success criteria

- `plan.md` created with measurable success criteria per phase.
- Validation phase included unless explicitly waived.
- Mode-specific outputs all written.

## Examples

```
/shannon:plan "Add SSO with Okta to admin panel"
/shannon:plan "Migrate from SQLite to Postgres" --phases 8
/shannon:plan "Real-time collaborative editing layer" --mode converge --rounds 5
/shannon:plan "Add OAuth2 with PKCE" --mode tournament --candidates 4
/shannon:plan "Add E2E encryption with key rotation" --mode deep
```
