# Phase 4 Summary — Hook curation (16 → 7) + required_hooks contract + scripts/doctor.py

**Outputs**:
- `v1/shannon/hooks/` (7 hook scripts + `_lib.js` + `hooks.json`)
- `v1/shannon/scripts/doctor.py` (the cross-check)
- 8 v1 skills with `required_hooks:` frontmatter added
- `commands/doctor.md` wired to `scripts/doctor.py`
- `cut-hooks.md`, `PHASE-04-VALIDATION.md`

## Headline

- **16 → 7** registered hook scripts (within ROADMAP gate range 5-9)
- **3 merged dispatchers** absorb 12 of the 16 inherited scripts:
  - `pre-edit-discipline.js` (read-before-edit + plan-before-execute)
  - `post-action-discipline.js` (validation-not-compilation + validation-skill-tripwire + completion-claim-validator + fab-pattern-detection + evidence-quality-check)
  - `observability.js` (hooks-fired-log + context-threshold-warn + task-list-tracker + skill-activation-check + session-context-inject)
- **4 standalone hooks** kept (block-fab-files, subagent-governance, evidence-gate, stop-semantics)
- **1 shared `_lib.js`** — replaces v7's `../lib/hook-runner` and `../core/layers/...` dependency tree with a self-contained 70-line helper
- **8 v1 skills** declare `required_hooks` — total 12 declared dependencies — all resolve to registered hooks
- **0 contract mismatches**

## What scripts/doctor.py validates

8 checks:
1. Plugin manifest present + valid JSON
2. Skills count in target range
3. Agents count in target range
4. Commands count in target range
5. Hooks count in target range
6. hooks.json registers real scripts
7. required_hooks contract (the central Phase 4 deliverable)
8. Agents `_built/` matches manifests (continued from Phase 2)

All 8 PASS with `mismatches: 0` on real disk.

## Why this matters

`/shannon:doctor` is now MECHANICAL. Any drift between skill declarations and hook registrations triggers a FAIL. The Phase 4 deliverable wasn't just "reduce hooks"; it was "make the contract checkable from disk." That's what the doctor does.

For Phase 5 (Validation harnesses), this means the SDK runner and Tmux runner can both invoke `/shannon:doctor` as a pre-flight check before running any benchmark. Contract drift = immediate failure, no theater.

## Iron Rule compliance highlights

- No `exit 0` stub hook scripts — every script has real body logic ported from the inherited equivalent.
- The contract check reads real disk every run — there is no cached "OK" result.
- Project opt-in gate (`/shannon:enforce on/off`) is honored at the helper level (`shannonActive()` in `_lib.js`) — hooks never pollute non-Shannon projects.

## Done condition

✓ 7 hooks in `v1/shannon/hooks/` (in 5-9 range)
✓ hooks.json valid + registers real scripts
✓ 8 skills declare required_hooks
✓ doctor.py exit 0; 0 mismatches
✓ commands/doctor.md wired to scripts/doctor.py
✓ cut-hooks.md documents 9 collapsed entry points + 6 intentionally-not-ported legacy scripts
✓ Phase 0+1+2+3 regression PASS (all verified by doctor.py)
