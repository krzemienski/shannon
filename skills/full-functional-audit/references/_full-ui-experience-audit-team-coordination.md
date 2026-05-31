# Team Coordination

> When full-ui-experience-audit runs in team mode (multiple sub-agents in parallel), how the lead coordinates them. Read only when mode=team in run-config.md.

## When team mode pays for itself

Solo mode = lead does every phase sequentially.
Team mode = lead dispatches workers in parallel.

Team-mode break-even is roughly **screens × interactions > 50**. Below that, coordination overhead exceeds parallelism savings.

Above that, team mode wins on wall-clock. But team mode also costs more
total tokens (lead + worker per slice) and has its own coordination failures.

## The lead's responsibilities

In team mode, the lead does NOT do per-screen audits. The lead:

1. Designs the slicing (which screens to which workers)
2. Dispatches workers (single-message multi-Task — see SKILL.md)
3. Receives worker reports
4. Resolves conflicts (workers fighting over shared resources)
5. Merges findings into the consolidated `findings.json`
6. Owns Phase 5 convergence decision and Phase 6 confirmation pass

The lead never delegates the final verdict. That's its job.

## Slicing

Slice the inventory so each worker gets:
- Non-overlapping work (no two workers auditing the same screen)
- Roughly equal work (so they finish near each other)
- Independent slices (no worker waits on another's output)

Slice strategies:

### Strategy: By screen

```
Worker 1: screens [Dashboard, Settings, Profile]
Worker 2: screens [Workflow, Inventory, Reports]
Worker 3: screens [Admin, Analytics, Help]
```

Simple. Works when screens have roughly equal complexity.

### Strategy: By priority + screen

```
Worker 1 (high-priority): P0 screens [Dashboard, Login, Onboarding]
Worker 2 (medium): P1 screens [Settings, Profile, Reports]
Worker 3 (low): P2 screens [Admin, Debug, Help]
```

Frees Worker 1 to go deep on high-impact screens; Worker 3 can be a junior
or use less-expensive model tier.

### Strategy: By phase

```
Worker 1: Phase 2 (UX audit) for all screens
Worker 2: Phase 3 (functional validation) for all interactions
Worker 3: Phase 4 (fixes) once findings accumulate
```

Useful when phases have very different skill profiles. Coordination is harder
(Worker 3 waits for Workers 1+2 to find things).

Default: by-screen for most runs.

## Single-message dispatch (non-negotiable)

When you dispatch the team, all `Task` tool calls go in ONE assistant message.

```
Single message:
  Task(subagent_type="general-purpose", description="Worker 1 screens", prompt="...")
  Task(subagent_type="general-purpose", description="Worker 2 screens", prompt="...")
  Task(subagent_type="general-purpose", description="Worker 3 screens", prompt="...")
```

Splitting across messages = sequential execution. The single-message rule comes from Claude Code's parallel-execution mandate (`agents/team-builder.md`).

## Worker prompt template

Each worker's prompt should be self-contained (workers have no shared context):

```
You are Worker N in a team-mode full-ui-experience-audit.

YOUR SLICE:
- Screens assigned: [list]
- Phases to run for those screens: 2 (UX audit), 3 (functional validation)
- DO NOT do Phase 4 (fixes) — that's the lead's call after seeing all workers' findings

INPUTS:
- audit-evidence/run-config.md
- audit-evidence/cycle-NN/inventory.md (your slice = the rows for your screens)
- audit-evidence/baseline/*.png (the cycle-1 baseline for diff)

OUTPUTS:
- audit-evidence/cycle-NN/captures/<screen>-*.png — your screens' captures
- audit-evidence/cycle-NN/findings.json — append your findings (be careful — see merge rules)

RESOURCE COORDINATION:
- Simulator: you have a MUTEX. Wait for the lead's signal before interacting.
- Browser: each worker gets its own tab (you = tab N). Don't navigate other tabs.
- Curl: read endpoints are PARALLEL; write endpoints are SERIAL — coordinate with lead.

CRITICAL RULES:
- Don't audit screens outside your slice — that's another worker's responsibility
- Don't modify SKILL.md files or commit changes — Phase 4 is the lead's job
- Report finishing immediately when your slice is complete

Begin Phase 2 + Phase 3 on your slice.
```

## findings.json merge

Multiple workers writing to the same `findings.json` is a race condition.

Two safe patterns:

### Pattern: Per-worker findings file, merge at end

```
Worker 1 writes: cycle-NN/workers/findings-worker-1.json
Worker 2 writes: cycle-NN/workers/findings-worker-2.json
Worker 3 writes: cycle-NN/workers/findings-worker-3.json

Lead merges: cycle-NN/findings.json = consolidated list with stable IDs
```

This is the recommended pattern. No race; ID assignment is deterministic in the lead's merge step.

### Pattern: File-locked findings.json

```
Each worker:
  flock cycle-NN/findings.json.lock
  read findings.json
  modify
  write back
  release lock
```

Works but slower (workers serialize on the lock). Avoid if Pattern 1 is feasible.

## Resource-mutex matrix

From the SKILL.md, repeated here for team-mode reference:

| Resource | Mutex policy |
|----------|--------------|
| iOS simulator | EXCLUSIVE — one worker at a time |
| Browser tab (same) | EXCLUSIVE per tab |
| Browser tab (different) | PARALLEL (one tab per worker) |
| Backend (read) | SHARED (parallel reads OK) |
| Backend (write) | SERIAL (writes coordinate via API contract) |
| Code edits same file | EXCLUSIVE |
| Code edits disjoint modules | PARALLEL |
| Curl on read endpoint | PARALLEL |
| Curl on write endpoint | SERIAL |
| Build process | EXCLUSIVE (shared output dir) |

Workers must obey these. The lead is the enforcer.

For iOS: assign all interactive Phase 3 work to ONE worker per cycle (simulator is exclusive). Other workers do Phase 2 capture from existing screenshots.

For web: each worker gets its own browser tab; coordinate per-tab navigation.

## Lead's merge protocol

After all workers report:

1. Read each `cycle-NN/workers/findings-worker-N.json`
2. Assign stable IDs to new findings (next-available F-c0(NN)-XXX)
3. Deduplicate (same defect found by multiple workers gets one entry; attribute discovery to first)
4. Sort by priority + severity
5. Write consolidated `cycle-NN/findings.json`
6. Write `cycle-NN/cycle-report.md` synthesizing all workers' captures

## When team mode fails gracefully

If a worker:
- Times out → lead retries with extended budget
- Reports an error → lead investigates; may take over the slice or assign to another worker
- Reports findings that overlap another worker's → lead deduplicates in merge
- Reports a SCOPE_VIOLATION (worked outside its slice) → lead reverts those changes, re-dispatches the worker with tighter prompt

If team-mode infrastructure itself fails (subagent tool unavailable, etc.):
- Fall back to solo mode for this cycle
- Tell the user
- Continue — solo mode is slower but correct

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| All-workers-edit-same-file | Race condition, lost work | Slice by screen / module |
| Lead also does worker work | Loses parallelism + confusion | Lead coordinates only |
| Dispatch in multiple messages | Sequential execution | Single message; one batch of Task calls |
| Workers commit code | Phase 4 is lead's | Workers report; lead applies |
| No mutex on simulator | Concurrent taps corrupt state | EXCLUSIVE mutex |

## Cross-references

- `skills/full-ui-experience-audit/` — parent skill (single-message rule)
- `references/phase-0-setup.md` — Phase 0 sets up the team
- `references/inventory-template.md` — what the slicing reads from
- `references/fix-loop-protocol.md` — Phase 4 lead-only work
- `agents/team-builder.md` — the dispatch primitive
- `agents/team-qa.md`, `agents/team-validator.md` — sibling team patterns
- `skills/dispatch-parallel/` — single-message dispatch enforcement
- `skills/multi-agent-patterns/` — design patterns for multi-agent work
