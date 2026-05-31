# Plan 04: Hook curation (16 → 7) + required_hooks contract + scripts/doctor.py

> **This PLAN.md is the execution prompt.** Single combined plan covering hook reduction, contract declaration, and doctor wiring. Same aggressive-merge pattern as Phases 1 and 3.

---

## Prerequisite check (BLOCKING)

```bash
test -f ../03-commands/PHASE-03-VALIDATION.md
grep -qE 'Verdict.*PASS' ../03-commands/PHASE-03-VALIDATION.md
[ $(ls ../../../commands/ | wc -l) -ge 13 ]
test -f ../02-agent-embedding/PHASE-02-VALIDATION.md
[ $(ls ../../../skills/ | wc -l) -eq 31 ]
```

---

## Mock detection preamble

REFUSED tasks:

- Writing hook scripts that exit 0 unconditionally (stubs).
- Adding `required_hooks:` entries that reference hooks not in v1/shannon/hooks/hooks.json.
- Skipping the doctor contract check.
- Claiming "merged" when the merged hook's body is just a passthrough to the absorbed scripts (no actual consolidation).

---

## Context

- **Phase**: 4 (Hook curation + contract)
- **Predecessor**: Phase 3 PASS (19 v1 commands; 0 phantom refs)
- **Inputs**:
  - 16 inherited registered hooks in parent `hooks/` + `hooks.json`
  - 31 v1 skills (8 of which have hook dependencies)
- **Outputs**:
  - `v1/shannon/hooks/` with 7 scripts + `hooks.json`
  - `required_hooks:` frontmatter on 8 v1 skills
  - `scripts/doctor.py` — cross-checks the contract
  - `cut-hooks.md`
  - `PHASE-04-VALIDATION.md`

## Decisions (per user blanket merge authorization)

### Keep standalone (4)

| v1 hook | Inherited script | Event |
|---|---|---|
| `block-fab-files.js` | block-fab-files.js | PreToolUse:Write\|Edit\|MultiEdit |
| `subagent-governance.js` | subagent-governance-inject.js (renamed) | PreToolUse:Task\|Agent |
| `evidence-gate.js` | evidence-gate-reminder.js (renamed) | PreToolUse:TaskUpdate |
| `stop-semantics.js` | stop-task-semantics.js (renamed) | Stop |

### Merge into dispatchers (3)

| v1 hook | Absorbs | Event |
|---|---|---|
| `pre-edit-discipline.js` | read-before-edit + plan-before-execute | PreToolUse:Edit\|MultiEdit\|Write |
| `post-action-discipline.js` | validation-not-compilation + validation-skill-tripwire + completion-claim-validator + fab-pattern-detection + evidence-quality-check | PostToolUse:Bash + PostToolUse:Edit\|Write\|MultiEdit |
| `observability.js` | hooks-fired-log + context-threshold-warn + task-list-tracker + skill-activation-check + session-context-inject | PostToolUse:* + PostToolUse:TaskCreate\|TaskUpdate + SessionStart + UserPromptSubmit |

### required_hooks contract (8 v1 skills)

| Skill | required_hooks |
|---|---|
| `no-fakes-discipline` | block-fab-files, post-action-discipline |
| `evidence-gate` | evidence-gate, post-action-discipline |
| `completion-gate` | evidence-gate, post-action-discipline |
| `functional-validation` | post-action-discipline |
| `dispatch-parallel` | subagent-governance |
| `multi-agent-patterns` | subagent-governance |
| `team-coordinator` | subagent-governance, stop-semantics |
| `refusal-discipline` | evidence-gate |

23 remaining skills declare `required_hooks: []` (or omit the field — doctor.py tolerates either).

## Tasks

### Task 1 — Write the 7 v1 hook scripts

Each script must have a META export at the top:

```js
// META
// name: <hook-name>
// event: <hook-event-list>
// consumed_by_skills: <comma-list>
// description: <one-line>
```

For standalone hooks (4): copy inherited script body, prepend META.

For merged hooks (3): write dispatcher logic that runs each absorbed check in sequence; any non-zero exit OR `decision: block` from any sub-check propagates.

**Verify (gate):**
- 7 scripts present in `v1/shannon/hooks/`
- Each has META export with `name`, `event`, `consumed_by_skills`
- Merged dispatchers reference the absorbed-check logic in their body (not stubs)

### Task 2 — Write v1 hooks.json

Single JSON registering all 7 v1 hooks with correct event matchers.

**Verify (gate):**
- `hooks.json` parses as valid JSON
- Every hook entry points to a real script in `v1/shannon/hooks/`
- Every hook event matcher matches Claude Code's hook event spec

### Task 3 — Add required_hooks to 8 skill frontmatters

For each skill with hook dependency: edit `v1/shannon/skills/<name>/SKILL.md` frontmatter to add `required_hooks: [<list>]`.

**Verify (gate):**
- All 8 edits applied
- Every `required_hooks` entry resolves to a real v1 hook in hooks.json
- Untouched skills' frontmatter unchanged

### Task 4 — Write scripts/doctor.py

Read every skill's `required_hooks` declaration; read hooks.json; cross-check.

**Output spec:**

```json
{
  "version": "0.1.0",
  "summary": {
    "skills_with_required_hooks": 8,
    "total_hook_dependencies": 14,
    "registered_hooks": 7,
    "mismatches": 0
  },
  "checks": [...],
  "mismatches": []
}
```

**Verify (gate):**
- `python3 scripts/doctor.py` exits 0
- Output JSON parses + summary shows mismatches: 0

### Task 5 — Wire commands/doctor.md to invoke scripts/doctor.py

The `/shannon:doctor` command body already exists from Phase 3. Add a "Implementation" section referencing `python3 scripts/doctor.py` so the command is runnable.

**Verify (gate):**
- `commands/doctor.md` body now references `scripts/doctor.py`

### Task 6 — Write cut-hooks.md

Document the 9 cut hook scripts: where their semantics moved.

**Verify (gate):**
- `cut-hooks.md` exists with 9 entries

## Phase-level regression check

```bash
# Phase 0+1+2+3
test -f ../../BRIEF.md
test -f ../../ROADMAP.md
test -f ../01-curation/PHASE-01-VALIDATION.md && [ $(ls ../../../skills/ | wc -l) -eq 31 ]
test -f ../02-agent-embedding/PHASE-02-VALIDATION.md && [ $(ls ../../../agents/ | wc -l) -eq 9 ]
test -f ../03-commands/PHASE-03-VALIDATION.md && [ $(ls ../../../commands/ | wc -l) -ge 13 ]
# Phase 2 build still passes
python3 ../../../build/verify-build.py | grep -q 'Mismatches: 0'
```

## Plan gate (BLOCKING)

Phase 4 PASSes when:

1. ✅ `v1/shannon/hooks/` count is 5-9 (target 7)
2. ✅ `v1/shannon/hooks/hooks.json` parses + registers all 7 hooks
3. ✅ Each hook script has META export
4. ✅ 8 skills declare `required_hooks` referencing real v1 hooks
5. ✅ `python3 scripts/doctor.py` exits 0 with 0 mismatches
6. ✅ `cut-hooks.md` documents 9 cuts
7. ✅ Phase 0+1+2+3 regression PASS

## Done condition

`PHASE-04-VALIDATION.md` with verdict=PASS. Phase 5 (Validation harnesses) unblocked.

## Iron Rule restatement

- Hook bodies are REAL — no exit-0 stubs.
- Merged dispatcher logic is REAL — each absorbed check executes.
- `required_hooks` only references hooks in v1 hooks.json — no phantoms.
- `doctor.py` reads disk; emits real JSON; 0 mismatches must be a real count.
