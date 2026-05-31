# Plan 03: Command consolidation (27 → 19)

> **This PLAN.md is the execution prompt.** Single combined plan (no sub-plans) per the aggressive-merge pattern used in Phase 1. User blanket authorization:
>
> > "You're allowed to merge what you're allowed to merge together. So you can order across all of them and something might be repetitive in theory or merge into your mind."

---

## Prerequisite check (BLOCKING)

```bash
# Phase 2 must PASS
test -f ../02-agent-embedding/PHASE-02-VALIDATION.md
grep -qE 'Verdict.*PASS' ../02-agent-embedding/PHASE-02-VALIDATION.md
[ $(ls ../../../agents/ | wc -l) -eq 9 ]
[ $(ls ../../../skills/ | wc -l) -eq 31 ]
test -f ../../../build/embed-skills.py
```

---

## Mock detection preamble

Any task that satisfies its gate by:

- writing a command body that references skills/agents not in v1's curated set,
- claiming "consolidated" without actually merging the absorbed commands' semantics into the kept command's body,
- producing stub command files with only frontmatter and no body,
- skipping the cut-commands.md rationale documentation,

is REFUSED.

---

## Context

- **Phase**: 3 (Command consolidation)
- **Predecessor**: Phase 2 PASS (9 agents + manifests + build + smoke-test all green)
- **Inputs**:
  - 27 inherited commands in parent `commands/` directory
  - 9 v1 agents in `v1/shannon/agents/`
  - 31 v1 skills in `v1/shannon/skills/`
- **Outputs**:
  - `v1/shannon/commands/` — 19 curated commands
  - `cut-commands.md` — 9 cut/absorbed commands with rationale
  - Phase 3 validation

## Decisions (per user blanket authorization)

| Action | Inherited commands | v1 result |
|---|---|---|
| **CONSOLIDATE 3 → 1** | `dispatch`, `dispatch-parallel`, `dispatch-competitive` | `/shannon:dispatch` with `mode: sequential\|parallel\|competitive` |
| **CONSOLIDATE 4 → 1** | `plan`, `plan-converge`, `plan-deep`, `plan-tournament` | `/shannon:plan` with `mode: linear\|converge\|tournament\|deep` |
| **CONSOLIDATE 2 → 1** | `audit`, `audit-completion` | `/shannon:audit` with `scope: live\|completion-evidence` |
| **CONSOLIDATE 2 → 1 (NEW)** | `enable`, `disable` | `/shannon:enforce <on\|off>` (new name; semantics preserved) |
| **CUT for v0.1.0** | `forge` | Overlap with `cook + oracle`; defer to v1.x |
| **KEEP individually** | audit, autopilot, cook, dispatch, doctor, fix, install, loop, plan, prd, reflect, research, resume, retro, team, trace, validate, why (18) | One file each in `v1/shannon/commands/` |

Final v1 surface: 18 inherited-kept + 1 new (`enforce`) = **19 commands**. Within ROADMAP gate range (13-20).

Cut/absorbed: 9 commands (dispatch-parallel, dispatch-competitive, plan-converge, plan-deep, plan-tournament, audit-completion, enable, disable, forge).

## Tasks

### Task 1 — Write the 19 v1 command files

For each kept command:

1. Read the inherited command body (parent `commands/<name>.md`)
2. Update references to skills/agents to point to v1 names (e.g., `validator` agent, `functional-validation` skill)
3. For consolidated commands, write a unified body covering all absorbed modes
4. For the new `enforce` command, write a fresh body merging enable+disable semantics

**Verify (gate):**
- `v1/shannon/commands/` contains exactly 19 `.md` files
- Each has frontmatter with `description` + `argument-hint` (optional)
- Each body references at least one real v1 agent OR v1 skill
- Consolidated commands explicitly handle each absorbed mode in their body

### Task 2 — Write cut-commands.md

Document the 9 cut commands:

- For each: which inherited command, what it did, where its semantics went (absorbed-into target OR deferred to v1.x with reason)

**Verify (gate):**
- `cut-commands.md` exists in this directory
- 9 cut entries; each has a one-paragraph rationale

### Task 3 — Resolution verification

Cross-check that every v1 command body's skill/agent references resolve:

```bash
# For each command's body, extract subagent_type=... and Skill: ... and verify they exist
python3 scripts/verify-command-resolution.py   # (built inline if not present)
```

**Verify (gate):**
- 0 unresolved references in any v1 command body

## Phase-level regression check

```bash
# Phase 0
test -f ../../BRIEF.md && test -f ../../ROADMAP.md && test -f ../../../DECISIONS.md
# Phase 1
test -f ../01-curation/PHASE-01-VALIDATION.md
[ $(ls ../../../skills/ | wc -l) -eq 31 ]
# Phase 2
test -f ../02-agent-embedding/PHASE-02-VALIDATION.md
[ $(ls ../../../agents/ | wc -l) -eq 9 ]
```

## Plan gate (BLOCKING)

Phase 3 PASSes when:

1. ✅ `v1/shannon/commands/` count is in 13-20 (target 19)
2. ✅ Every kept command file has valid frontmatter + non-empty body
3. ✅ Every command body references a real v1 agent or skill (0 phantom references)
4. ✅ `cut-commands.md` documents 9 cuts with rationale
5. ✅ Consolidation tables: each absorbed command's semantics surface in the absorbing command's body
6. ✅ Phase 0 + Phase 1 + Phase 2 regression PASS

## Done condition

`PHASE-03-VALIDATION.md` with verdict=PASS. Phase 4 (Hook curation) unblocked.

## Iron Rule restatement

- Only real v1 skills/agents referenced in command bodies — no phantoms
- Each consolidated command actually merges semantics (no "see also" stub)
- Cuts are deliberate; rationale written, not "we don't need it"
