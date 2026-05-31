# Patch: Brownfield planning capability

**Date**: 2026-05-28
**Status**: ✅ Applied; all gates green; release-candidate updated
**Scope**: User-facing capability gap identified after Phase 7 structural PASS

## The gap

After Phase 7 release-candidate was complete, the user observed:

> "did we lose the deep planning ability where on brownfield projects we analyze all code, find all users skills for the code and the tasks, write functional plans etc"

Honest answer: **partially yes**. The building blocks were preserved (`Skill: codebase-analysis` is in v1), but the user-facing workflow that orchestrates them was not. Specifically:

1. `/shannon:plan` and `/shannon:cook` went brief → planner → executor with no pre-execution codebase survey
2. `/shannon:forge` (the v7 10-phase pipeline that started with codebase-analysis) was deferred to v1.x in Phase 3
3. No skill or command inventoried the user's installed skills/plugins to map them to a task
4. `Skill: codebase-analysis` SKILL.md still referenced the cut `/shannon:forge` command (stale reference)

## What this patch ships

### 1. New skill: `skills/skill-inventory/SKILL.md`

Discovers what the user's environment actually offers (Shannon skills + other plugins' skills + MCP tools) and maps it to the task at hand. Calls `mcp__skills__list_skills` + `mcp__plugins__list_plugins` + (if available) `mcp__skills__suggest_skills`; writes structured findings to `reports/skill-inventory-<run-id>.md`.

Iron Rule discipline: only lists what the runtime MCP calls actually returned — no fabricated recommendations.

### 2. New command: `/shannon:scope`

Brownfield reconnaissance phase. Read-only. Runs three parallel streams:

- Stream 1: `Skill: codebase-analysis` (5 parallel scientists — inventory + deps + entry-points + proving-cmds + module-map)
- Stream 2: `Skill: skill-inventory`
- Stream 3: `Skill: observability-report` (recent session context)

Then `Task: planner` synthesizes `scope-report.md` cross-citing all three streams. Feeds `/shannon:plan --mode brownfield` or `/shannon:cook --brownfield`.

### 3. New mode: `/shannon:plan --mode brownfield`

Auto-runs `/shannon:scope` first; planner uses the scope-report as input. Plan cites specific files (from inventory), specific skills (from skill-inventory), specific proving-commands (from codebase-analysis Stream 4).

### 4. New flag: `/shannon:cook --brownfield`

Same scope→plan→execute chain at the cook level. Mandatory recommendation for any non-trivial change on existing code.

### 5. Updated agent: `planner` now embeds `codebase-analysis` + `skill-inventory`

Manifest: 5 → 7 embedded skills. Planner now has brownfield-survey capability baked into its spawn context — no `Skill:` round-trip needed when handling brownfield work.

### 6. Swept 37 stale `/shannon:forge` references

All `/shannon:forge` mentions across 14 files (6 skills + 8 AGENT.md files) replaced with context-aware v1 references:

- "Phase 1 of /shannon:forge" → "Stream 1 of /shannon:scope"
- "Phase 2 of /shannon:forge" → "documentation research mode"
- "Phase 3-10 of /shannon:forge" → corresponding step in `/shannon:cook` / `/shannon:cook --mode consensus`
- Generic "/shannon:forge" → "/shannon:cook --brownfield"

Verified: 0 `/shannon:forge` references remain in v1 source.

## Verification

| Check | Before | After |
|---|---|---|
| Skills count | 31 | **32** (within gate 25-35) |
| Commands count | 19 | **20** (within gate 13-20) |
| Agents count | 9 | **9** (unchanged) |
| Hooks count | 7 | **7** (unchanged) |
| `build/verify-build.py` mismatches | 0 | **0** |
| `scripts/doctor.py` checks_fail / mismatches | 0 / 0 | **0 / 0** |
| `bash scripts/harness/run-all.sh --dry-run` | exit 0 | **exit 0** |
| Phantom references across commands | 0 | **0** |
| `/shannon:forge` references in v1 source | 75 | **0** |
| Planner embedded skills | 5 | **7** |
| Build embedding relationships | 32 | **34** |

## Doctor output (after patch)

```json
{
  "summary": {
    "skills_with_required_hooks": 8,
    "total_hook_dependencies": 12,
    "registered_hooks": 7,
    "checks_pass": 8,
    "checks_fail": 0,
    "mismatches": 0
  }
}
```

All 8 checks PASS, including:

- Skills count: 32 (in 25-35)
- Commands count: 20 (in 13-20)
- required_hooks contract: 12 dependencies, all resolve
- Agents `_built/` matches manifest: 34 total relationships (added codebase-analysis + skill-inventory to planner)

## Iron Rule compliance

- The new `Skill: skill-inventory` refuses to fabricate skill recommendations — it only lists what `mcp__skills__list_skills` actually returned. If the MCP tool is unavailable, it writes `REFUSAL.md` rather than guessing.
- The new `/shannon:scope` runs read-only — no edits made to source during reconnaissance.
- The forge-reference sweep used context-aware substitution; no blanket find/replace. Each replacement preserved the semantic intent (Phase 1 of forge → Stream 1 of scope; Phase 10 of forge → final completion gate in cook).
- `Skill: codebase-analysis` is now invocable both standalone AND from `/shannon:scope`. Its body explicitly says so.

## What's still NOT in v0.1.1

- **Oracle review** — the pre-execution + post-execution oracle-quorum review (Phases 4 + 9 of legacy forge). Approximated by `Task: critic` in `/shannon:cook`. True 3-oracle quorum reserved for v1.x if user feedback shows the simpler critic-based approach is insufficient.
- **Skill-inventory caching** — the runtime MCP calls happen fresh each time. v1.x could add a session-level cache.
- **Automatic `--brownfield` detection** — currently the user must opt in via flag. v1.x could auto-detect "this is brownfield" from a non-empty git history + the absence of a recent scope-report.

## Cross-references

- `commands/scope.md` — new command body
- `skills/skill-inventory/SKILL.md` — new skill
- `agents/planner/manifest.yml` — now embeds codebase-analysis + skill-inventory
- `agents/planner/AGENT.md` — re-built with two new inlined SKILL.md bodies
- `commands/plan.md` — `--mode brownfield` documented
- `commands/cook.md` — `--brownfield` flag documented
- `docs/SKILLS_CATALOG.md` — regenerated with 32 skills
- `RELEASE_NOTES.md` — updated to reflect v0.1.1 patch

## Done condition

✓ All gates pass (build, verify-build, doctor, harness --dry-run)
✓ 0 phantom references; 0 stale forge mentions
✓ New capability exercised structurally (commands and skills loaded by doctor + harness)
✓ Release-candidate updated; RELEASE_NOTES.md describes the brownfield workflow
