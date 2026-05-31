# Phase 4 — Cut / absorbed hooks

The 16 inherited hooks were consolidated to 7 v1 hooks. 9 of the inherited scripts have their behavior preserved inside merged dispatchers; their entry points were collapsed.

## Renamed (kept; new name for clarity)

| Inherited | v1 name |
|---|---|
| `subagent-governance-inject.js` | `subagent-governance.js` |
| `evidence-gate-reminder.js` | `evidence-gate.js` |
| `stop-task-semantics.js` | `stop-semantics.js` |

Behavior preserved; the `-inject`/`-reminder`/`-semantics` suffixes were inconsistent across the v7 set.

## Absorbed into merged dispatchers (9)

### Into `pre-edit-discipline.js` (2 inherited)

| Inherited script | Where its logic lives now |
|---|---|
| `read-before-edit.js` | `pre-edit-discipline.js` → `checkReadBeforeEdit()` |
| `plan-before-execute.js` | `pre-edit-discipline.js` → `checkPlanBeforeExecute()` |

Rationale: both are PreToolUse:Edit advisory reminders. Running them as one dispatcher eliminates two stdin-payload reads per Edit call.

### Into `post-action-discipline.js` (5 inherited)

| Inherited script | Where its logic lives now |
|---|---|
| `validation-not-compilation.js` | `post-action-discipline.js` → `runBashChecks()` (BUILD_CMDS + BUILD_SUCCESS branch) |
| `validation-skill-tripwire.js` | `post-action-discipline.js` → `runBashChecks()` (tripwire append + stderr) |
| `completion-claim-validator.js` | `post-action-discipline.js` → `runBashChecks()` (CLAIM regex branch) |
| `fab-pattern-detection.js` | `post-action-discipline.js` → `runEditWriteChecks()` (FAB_HINTS branch) |
| `evidence-quality-check.js` | `post-action-discipline.js` → `runEditWriteChecks()` (0-byte evidence branch) |

Rationale: 5 inherited scripts all fired on PostToolUse events. Merging into one dispatcher with `tool === 'Bash'` vs `tool in ['Edit','Write','MultiEdit']` branches cuts 4 process spawns per tool call.

### Into `observability.js` (5 inherited)

| Inherited script | Where its logic lives now |
|---|---|
| `hooks-fired-log.js` | `observability.js` → `appendHookLog()` |
| `context-threshold-warn.js` | `observability.js` → `contextWarning()` |
| `task-list-tracker.js` | `observability.js` → `appendOpenTask()` + `removeOpenTask()` |
| `skill-activation-check.js` | `observability.js` → `skillHints()` |
| `session-context-inject.cjs` | `observability.js` → `SessionStart` branch (appendHookLog) |

Rationale: all 5 are observability-side concerns. They fire on different events (SessionStart, UserPromptSubmit, PostToolUse:*, PostToolUse:TaskCreate|TaskUpdate). One script registered against all those events with event-branching dispatch is materially simpler and faster.

## Verification

- Inherited registered hooks (from `hooks.json`): **16** entry points (in `commands/audit-skill-tripwire.js` counts as 1, etc.).
- v1 registered hooks: **7** entry points.
- 16 − 7 = 9 entry points collapsed.
- 12 inherited script behaviors absorbed into 3 merged dispatchers.
- All inherited behaviors preserved (no functionality cut).

## Non-registered v7 scripts intentionally NOT ported

These v7 hook directory files were NOT registered in v7's `hooks.json` and are NOT ported to v1:

- `post_tool_use.py`, `precompact.py`, `session_start.sh`, `stop.py`, `user-prompt-submit-hook.sh`, `user_prompt_submit.py`

These were exploration / legacy scripts in the v7 repo. v1 starts fresh with only the 7 dispatchers above.

## Iron Rule compliance

- Every merged dispatcher contains the actual logic from the absorbed scripts (verified by reading both source bodies and the merged body — not a "see above" pointer).
- The `required_hooks` contract on 8 skills references only the 7 v1 hooks (verified by `scripts/doctor.py` which exits 0 with 0 mismatches).
- No "deferred" hooks: every inherited behavior either lives in a v1 hook or was intentionally not ported per the table above.
