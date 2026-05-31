# Phase 4 — VALIDATION

**Phase**: 4 (Hook curation + required_hooks contract + /shannon:doctor)
**Verdict**: ✅ **PASS** — 16 inherited hooks consolidated to 7 v1 hooks; contract enforced by working doctor.py.
**Date**: 2026-05-28

## ROADMAP gate criteria

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | `v1/shannon/hooks/` count is 5-9 | ✅ PASS | 7 hook scripts + `_lib.js` + `hooks.json` |
| 2 | Every kept hook has META export | ✅ PASS | All 7 scripts have `// META\\n// name:\\n// event:\\n// consumed_by_skills:\\n// description:` block |
| 3 | Every skill that depends on a hook declares it in `required_hooks` | ✅ PASS | 8 skills, 12 total declared dependencies, all resolved (doctor.py contract check PASS) |
| 4 | `python3 scripts/doctor.py` exits 0 (no mismatches) | ✅ PASS | exit code 0; `summary.mismatches: 0`; all 8 checks PASS |
| 5 | `/shannon:doctor` returns a structured report | ✅ PASS | `commands/doctor.md` wired to `scripts/doctor.py`; JSON output spec in body |
| 6 | Phase 0 + Phase 1 + Phase 2 + Phase 3 regression PASS | ✅ PASS | doctor.py's check-2/3/4/5 + verify-build all green |

## Headline numbers

- **7 v1 hooks** (in `v1/shannon/hooks/` + 1 shared `_lib.js`)
- **9 inherited entry points collapsed** (16 → 7)
- **12 inherited script behaviors absorbed** into 3 merged dispatchers
- **8 v1 skills** declare `required_hooks`
- **12 total skill→hook dependencies**, all resolved
- **0 contract mismatches**
- **0 phantom hook references**

## v1 hook surface

| Hook | Event matcher | Consumed by skills |
|---|---|---|
| `block-fab-files.js` | PreToolUse:Write\|Edit\|MultiEdit | no-fakes-discipline |
| `pre-edit-discipline.js` | PreToolUse:Edit\|MultiEdit\|Write | (advisory; no required_hooks) |
| `subagent-governance.js` | PreToolUse:Task\|Agent | dispatch-parallel, multi-agent-patterns, team-coordinator |
| `evidence-gate.js` | PreToolUse:TaskUpdate | evidence-gate, completion-gate, refusal-discipline |
| `post-action-discipline.js` | PostToolUse:Bash\|Edit\|Write\|MultiEdit | no-fakes-discipline, evidence-gate, completion-gate, functional-validation |
| `observability.js` | SessionStart + UserPromptSubmit + PostToolUse:* + PostToolUse:TaskCreate\|TaskUpdate | (passive observability; no required_hooks) |
| `stop-semantics.js` | Stop | team-coordinator |

## scripts/doctor.py output

```json
{
  "summary": {
    "skills_with_required_hooks": 8,
    "total_hook_dependencies": 12,
    "registered_hooks": 7,
    "checks_pass": 8,
    "checks_fail": 0,
    "mismatches": 0
  },
  ...
}
```

All 8 checks PASS:
1. Plugin manifest present + valid JSON
2. Skills count in 25-35 (value=31)
3. Agents count in 5-12 (value=9)
4. Commands count in 13-20 (value=19)
5. Hooks count in 5-9 (value=7)
6. hooks.json registers real scripts (7 registered, 0 missing)
7. required_hooks → registered hooks (12 dependencies, 0 mismatches)
8. Agents _built/ matches manifest (32 embedding relationships, 0 mismatches)

## Implementation notes

### Sandbox-safe rewrite of inherited scripts

The inherited v7 hook scripts depended on `../lib/hook-runner` and `../core/layers/...` modules from the v7 plugin tree. For v1's standalone-plugin goal, these were replaced by a single self-contained `hooks/_lib.js` with minimal `runHook`, `shannonActive` (project opt-in gate), and `logError` helpers. Every v1 hook script `require('./_lib.js')` and runs the inherited check logic inline — no external module tree.

### Project opt-in gate respected

All v1 hooks short-circuit to `exit 0` unless `.shannon/active` is present in the project root (or `SHANNON_GLOBAL=1` is set). This preserves the v7 "default off; explicit opt-in via `/shannon:enforce on`" semantic that the user originally required.

### Merge dispatcher structure

The 3 merged dispatchers branch by event/tool inside `runHook`:

- `pre-edit-discipline.js`: calls `checkReadBeforeEdit()` and `checkPlanBeforeExecute()`; aggregates non-null messages into a single stderr write.
- `post-action-discipline.js`: branches on `tool === 'Bash'` vs `tool in [Edit, Write, MultiEdit]`; runs the appropriate subset of the 5 absorbed checks.
- `observability.js`: branches on `hook_event_name === SessionStart | UserPromptSubmit | PostToolUse`; runs the appropriate absorbed check(s) per branch.

## Iron Rule compliance

- Every hook script has a real body (no `exit 0` stubs). Verified by `wc -c` showing >800 bytes per script and by `node -c` syntax check passing on all 8 files.
- `scripts/doctor.py` reads real disk every check — `Mismatches: 0` is computed, not hard-coded.
- The contract is bidirectional: a phantom `required_hooks: [X]` in a skill would trigger contract-check FAIL; a hook script referenced by `hooks.json` but missing on disk would trigger hooks-json check FAIL. Both validated against the actual on-disk state.

## Phase regression check (at end of Phase 4)

```
Phase 0 BRIEF.md            ✓
Phase 0 ROADMAP.md          ✓
Phase 0 DECISIONS.md        ✓
Phase 1 PHASE-01-VALIDATION ✓
Phase 1: 31 skills          ✓ (doctor check value=31)
Phase 2 PHASE-02-VALIDATION ✓
Phase 2: 9 agents           ✓ (doctor check value=9)
Phase 2: build state        ✓ (doctor check 0 mismatches)
Phase 3 PHASE-03-VALIDATION ✓
Phase 3: 19 commands        ✓ (doctor check value=19)
```

## Done condition

`PHASE-04-VALIDATION.md` written (this file). Phase 5 (SDK + Tmux validation harnesses) unblocked.
