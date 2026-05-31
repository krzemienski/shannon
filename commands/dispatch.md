---
name: dispatch
description: "Subagent dispatch with mode flag. Sequential | parallel | competitive. Each subagent gets IRON-RULE inject; judge confirms output."
argument-hint: "<task-list-path | inline-tasks> [--mode sequential|parallel|competitive] [--max-parallel N] [--candidates N]"
---

# /shannon:dispatch

Subagent dispatch. Three modes consolidated:

> v1 consolidation: absorbs legacy `/shannon:dispatch-parallel` (`--mode parallel`) and `/shannon:dispatch-competitive` (`--mode competitive`).

## Inputs

- Positional: task list (path or newline-separated inline)
- `--mode sequential|parallel|competitive` (default `sequential`)
- `--max-parallel N` — concurrency cap for `parallel` mode (default 5)
- `--candidates N` — candidate count for `competitive` mode (default 3)

## Behavior

### mode=sequential
Sequential chain. Each step's output informs the next.

1. Parse task list.
2. For task 1..N:
   - Spawn `Task: executor` (or task-specified agent).
   - Wait for completion.
   - Invoke `Skill: judge` on output → PASS/FAIL/NEEDS_REVISION.
   - PASS → proceed. FAIL → halt. NEEDS_REVISION → re-dispatch with feedback (max 2 rounds).
3. Aggregate output to `reports/dispatch-seq-<run-id>.md`.

### mode=parallel
Parallel fan-out. Tasks must be independent (file-ownership separated).

1. Group tasks into batches of `--max-parallel`.
2. Per batch: spawn all `Task: executor` in parallel via **single message with multiple Task tool calls** (per `Skill: dispatch-parallel`).
3. Invoke `Skill: judge` on each output.
4. After all batches: `Task: meta-judge` reads ALL outputs → cross-subagent consistency check → final verdict.
5. Aggregate to `reports/dispatch-par-<run-id>.md`.

### mode=competitive
N agents attempt the SAME task; judges select the best.

1. Spawn `--candidates` `Task: executor` in parallel; each gets identical task, isolated output dir.
2. Wait for all to complete.
3. Invoke `Skill: judge` per candidate → individual scores.
4. Spawn `Task: meta-judge` with `Skill: consensus-engine` → debate-based ranking with cited reasoning.
5. Promote winning candidate; archive losers under `_rejected/`.
6. Aggregate to `reports/dispatch-comp-<run-id>.md`.

## Skills + agents

- `Skill: dispatch-parallel` (canonical single-message multi-Task pattern)
- `Skill: multi-agent-patterns`
- `Skill: tree-of-thoughts` (competitive mode — branching candidate options)
- `Skill: judge`
- `Skill: consensus-engine` (competitive mode)
- `Task: executor` (workers)
- `Task: meta-judge` (parallel/competitive synthesis)

## Iron rules

- Tasks in parallel mode MUST be independent (file ownership separates them).
- Meta-judge reads ALL outputs before emitting verdict.
- Competitive losers archived (never deleted) — they're considered-alternatives evidence.

## Examples

```
/shannon:dispatch tasks.md
/shannon:dispatch "fix file-a.ts" "fix file-b.ts" "fix file-c.ts" --mode parallel
/shannon:dispatch "Draft hero copy" --mode competitive --candidates 4
```
