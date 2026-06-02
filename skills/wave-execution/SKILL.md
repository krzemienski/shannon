---
name: wave-execution
description: The DeepPlan execution doctrine for running a multi-phase plan as dependency-ordered PARALLEL waves. INVOKE THIS SKILL — do NOT improvise wave execution from memory. The load-bearing mechanics are exactly what a freelanced run gets WRONG — (1) every agent in a wave MUST be spawned in ONE message — improvised runs spawn one agent per message, which is silently SEQUENTIAL with zero speedup; (2) a between-wave synthesis + validation gate MUST run before the next wave — improvised runs skip it and let conflicts/missing-integrations through; (3) a shared-context handoff file MUST be written first — improvised runs start agents blind. ALWAYS use when executing or running a multi-phase / multi-wave plan in parallel, when the user says "execute this phase plan in dependency waves", "run the plan phases as parallel waves", "decompose this plan into dependency-ordered waves", "wave-execute the plan", or when /shannon:plan --mode deep emits a wave plan. Shares context via the on-disk evidence tree (not Serena). NOT for single-task or strictly-sequential work, and NOT generic autopilot/team dispatch. NO MOCKS in any wave deliverable.
triggers:
  - "execute this phase plan in dependency waves"
  - "run the plan phases as parallel waves"
  - "decompose this plan into dependency-ordered waves"
  - "wave-execute the plan"
  - "spawn each wave of agents in parallel with a synthesis gate between waves"
---

# wave-execution

DeepPlan's execution doctrine. Think in waves, spawn in parallel, share context via the evidence tree, validate between waves.

## Why invoke this skill — never improvise wave execution

Decomposing a plan into dependency waves *looks* simple, so the natural instinct is to read the phase files and start executing by hand. That instinct produces a broken wave run every time, because the three mechanics that make waves actually parallel and safe are precisely the ones an improvised run drops:

| Improvised (wrong) | This skill (correct) |
|---|---|
| Spawns one agent per message → **silently sequential**, zero speedup | ALL agents in a wave in ONE message → true `max()` parallelism |
| Skips the between-wave gate → conflicts & missing integrations slip through | Mandatory synthesis + validation gate before the next wave |
| Starts agents with no shared context → divergent, duplicated work | Writes `wave-context.md` handoff first; every agent reads it |

If you are about to "just decompose the plan and run it," STOP and invoke this skill — the protocol below is the part you would otherwise get wrong.

> **Provenance / adaptation:** Ported from legacy `modes/WAVE_EXECUTION.md` (Shannon V3). The legacy version hard-required the Serena MCP for context sharing. This version replaces Serena with Shannon's on-disk **evidence tree + `.shannon/state/`** (per D3 — no Memory/Serena dependency). Behavior is otherwise preserved: dependency-grouped waves, one-message parallel spawn, per-wave synthesis gate.

## Mental model

```
Sequential:  T1 → T2 → T3 → T4          time = sum(all)
Wave:        W1[T1,T4] ▶ W2[T2,T3] ▶ …  time = sum(max per wave)   ~2-3x faster
```

## Prerequisites (hard)

Wave execution CANNOT start without:
1. A spec/complexity analysis (from `codebase-analysis` or `plan-author`).
2. A detailed phase plan (`plan-author` output: `plans/<run>/phase-NN-*.md`).

If missing: instruct the user to run `/shannon:plan --mode deep` first. Do not improvise a plan inside the executor.

## Protocol

1. **ANALYZE** — read the phase plan; build a dependency graph from each task's `blockedBy`.
2. **GROUP** — partition tasks into waves: a wave = all tasks whose dependencies are already satisfied. Maximize agents per wave, minimize wave count.
3. **LOAD** — write shared context to `.shannon/state/wave-context.md` (spec summary, architecture, prior-wave results). Every agent reads it.
4. **SPAWN** — execute ALL agents in a wave in ONE message (multiple Task/Agent invocations in a single response). This is the load-bearing rule for true parallelism — duration becomes `max(agent_times)`, not `sum`.
5. **VALIDATE** — after the wave returns, synthesize: aggregate deliverables, cross-check for conflicts / missing integrations / duplicate work / NO-MOCKS compliance. Write `evidence/waves/<run>/wave-NN-synthesis.md`.
6. **CHECKPOINT** — record wave completion + next-wave context in `.shannon/state/`.
7. **ITERATE** — proceed to the next wave only after the prior wave's synthesis gate passes.

## Context-loading protocol (every agent prompt MUST include)

```
Before your task, read:
- .shannon/state/wave-context.md   (spec + architecture + what we are building)
- evidence/waves/<run>/wave-<N-1>-synthesis.md  (prior wave results, if any)
Confirm you understand: what we build, how it is designed, what is already done, your scoped task.
```

## Correct vs incorrect spawn

- ✅ ONE message, N Task invocations → agents run simultaneously.
- ❌ N messages, one Task each → sequential, no speedup.

## Quality gates (per wave)

- All agents in the wave spawned in one message (true parallelism).
- Deliverables aggregated; integration points cross-validated.
- NO MOCKS: `grep -rE "mock|stub|fake|spy" <new code>` returns nothing in deliverables.
- Synthesis written + user-validation gate before the next wave.

## When NOT to use

- Single-task or strictly-sequential work (no parallel opportunity).
- Lightweight `/shannon:cook` runs below the complexity threshold.

## Iron rules

- Never spawn wave agents across multiple messages.
- Never let an agent start without the context-loading protocol.
- Never skip the between-wave synthesis gate.
- Never import or accept mocked deliverables.
