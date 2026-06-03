---
name: plan-deep
description: "Alias for /shannon:plan --mode deep — the deepest-plan treatment. ALWAYS runs codebase-analysis + skill-inventory first (non-skippable on brownfield), then deepplan-architect → tournament → convergence → validation-gate injection → wave decomposition. Identical machinery to /shannon:plan --mode deep; this is the named shortcut."
replaces:
  - /deepest-plan:deepest
  - /deepest-plan:deepest-plan
argument-hint: "<problem> [--candidates N] [--rounds N] [--phases N] [--greenfield]"
---

# /shannon:plan-deep

**This command is a pure alias.** `/shannon:plan-deep <problem>` is exactly
`/shannon:plan <problem> --mode deep` — same pre-flight, same agent, same skills,
same outputs. It exists only as the named shortcut that legacy `/deepest-plan:*`
users reach for. There is no separate implementation here: the single source of
truth is `commands/plan.md` (`--mode deep`), so this path can never silently
diverge or skip codebase analysis.

## What you get (inherited verbatim from `/shannon:plan --mode deep`)

### Step 0 — Codebase + skill pre-flight (GUARANTEED, non-skippable on brownfield)
Because plan-deep delegates to `/shannon:plan`, it inherits Step 0 unconditionally:
1. **Detect codebase** (`.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, non-empty `src/`/`lib/`/`app/`).
2. **`/shannon:scope`** auto-invoked — three parallel streams: `Skill: codebase-analysis`
   (5 parallel scientists), `Skill: skill-inventory`, `Skill: observability-report`.
3. Plan is grounded in the scope-report — every task cites a real file/module or a real skill.

Codebase analysis is the floor, not a feature (user CLAUDE.md MANDATORY CODE BASE
ANALYSIS rule). The only opt-out is `--greenfield` for a genuinely empty repo, which
still runs `skill-inventory` and only omits `codebase-analysis` (no code to read).

### Step 1 — Deep pipeline (`--mode deep`)
1. Dispatch `Task: shannon:deepplan-architect` (its frontmatter inherits
   `plan-author, codebase-analysis, skill-inventory, wave-execution` — all resolvable).
2. **Tournament** — N parallel `Task: shannon:planner` candidates, distinct
   perspectives; each reviewed by `Task: shannon:critic`; `Skill: judge` ranks.
3. **Convergence** — feed the tournament winner through 2-3 critique→revise rounds.
4. **Validation-gate injection** — `Skill: plan-author` in gate mode adds an explicit
   PASS-criteria + required-evidence gate to every phase.
5. **Wave decomposition** — `Skill: wave-execution` partitions the final phase plan
   into dependency-ordered waves (each wave = tasks whose `blockedBy` is satisfied)
   so `/shannon:cook` / `executor` spawns each wave's agents in one message.
6. Synthesize final plan + wave map; archive intermediate rounds under `_history/`.

## Flags (forwarded verbatim to `/shannon:plan --mode deep`)

Only flags the canonical command honors are exposed — a true alias invents nothing:

| plan-deep flag | forwarded to `/shannon:plan --mode deep` |
|---|---|
| `--candidates N` | tournament candidate count (default 3) |
| `--rounds N`     | convergence round count (default 3) |
| `--phases N`     | target phase count for the authored plan |
| `--greenfield`   | skip `codebase-analysis` pre-flight (empty repo ONLY) |

**Legacy `/deepest-plan:*` flag mapping (back-compat, no new machinery):**
- `--synthesis N` → accepted as an alias for `--candidates N`.
- `--debate` → **no-op / already-on.** The deep pipeline ALWAYS runs adversarial
  `shannon:critic` review across every tournament candidate and every convergence
  round, so the legacy "debate" behavior is the default. The flag is accepted and
  ignored for back-compat — it gates nothing, because `plan.md --mode deep` has no
  such toggle.

## Skills + agents (all resolvable — verified)

- `Task: shannon:deepplan-architect` (the deep planner; exists at `agents/deepplan-architect.md`)
- `Task: shannon:planner`, `Task: shannon:critic` (exist at `agents/`)
- `Skill: codebase-analysis`, `Skill: skill-inventory` (the guaranteed pre-flight)
- `Skill: plan-author` (authoring + gate injection)
- `Skill: wave-execution` (dependency-wave decomposition)
- `Skill: judge` (tournament ranking)
- `Skill: consensus-engine` (deep synthesis)

> NOTE: there are NO `plan-tournament` / `plan-converge` / `red-teamer` skills —
> tournament and converge are **modes** of `/shannon:plan`, and red-team review is the
> `shannon:critic` agent. (The pre-rewrite draft referenced those phantom skills and
> omitted codebase-analysis; both defects are fixed by making this a real alias.)

## Success criteria

- Resolves identically to `/shannon:plan --mode deep` (one source of truth).
- Codebase-analysis pre-flight runs on every brownfield invocation.
- Final plan: validation gate per phase + a dependency-ordered wave map.
- Every referenced skill/agent resolves to a real file (no phantom refs).
- Intermediate rounds archived under `_history/`.

## Examples

```
/shannon:plan-deep "Add E2E encryption to chat with key rotation"
/shannon:plan-deep "Multi-region failover" --candidates 4 --debate
# identical to:
/shannon:plan "Add E2E encryption to chat with key rotation" --mode deep
```
