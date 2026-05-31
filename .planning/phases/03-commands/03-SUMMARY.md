# Phase 3 Summary — Command consolidation (27 → 19)

**Output**: 19 v1 commands at `v1/shannon/commands/`; `cut-commands.md`; PHASE-03-VALIDATION.md.

## Headline

- **27 inherited → 19 v1** (within ROADMAP gate range 13-20)
- **8 commands absorbed** via mode-flag consolidation into existing entry points
- **1 command (forge) deferred** to v1.x with documented re-introduction condition
- **1 new command (enforce)** merging enable+disable into one mode-flagged toggle
- **31/31 v1 skills referenced** across the command set
- **9/9 v1 agents referenced** across the command set
- **0 phantom references**

## Consolidation pattern

The mode-flag pattern, validated in Phase 3 and consistent with the aggressive-merge pattern from Phase 1:

```
Legacy 1, 2, 3 → /shannon:cmd --mode A | B | C
```

Three commands collapse to one user-facing entry. Each mode preserves the absorbed legacy command's behavior in its own section of the body. No semantics lost.

## Why this matters

Each command's body now references the v1 skill and agent surface explicitly. When Phase 4 wires hooks to declare which skills they support, the cross-reference graph from commands → skills → hooks will be fully resolvable from disk. That's what enables `/shannon:doctor` (Phase 4 deliverable) to detect contract drift mechanically.

## What unblocks Phase 4

ROADMAP Phase 4 (Hook curation):
- 14 inherited hooks → 6-8 v1 hooks
- Each kept hook gets a META export declaring `name`, `event`, `consumed_by_skills`
- Each skill that depends on a hook declares it via `required_hooks: [name]` in its frontmatter
- `/shannon:doctor` (built in Phase 3 as a command, body wired in Phase 4) reads both sides and reports mismatches

## Done condition

✓ 19 commands in `v1/shannon/commands/`
✓ 0 phantom references
✓ cut-commands.md documents 9 cuts with rationale
✓ PHASE-03-VALIDATION.md verdict=PASS
✓ Regression: Phases 0+1+2 all still pass
