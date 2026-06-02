---
name: team
description: "Spawn coordinated multi-agent teammates with shared TaskList, charter-driven roles, file-ownership boundaries, stop-task semantics."
argument-hint: "<team-name> --charter <file> [--size N]"
---

# /shannon:team

Multi-teammate orchestration. Lead spawns N parallel teammates with file-ownership boundaries and a shared TaskList.

## Inputs

- `<team-name>` — slug; identifies team config dir under `.shannon/teams/<team-name>/`
- `--charter <file>` — required; markdown charter defining roles, file ownership, success criteria
- `--size N` — number of teammates (default from charter; max 8)

## Behavior

1. Parse charter; resolve roles, per-teammate file-ownership globs, dispatch graph.
2. `Task: shannon:team-builder` (lead) reads charter; creates TaskList entries.
3. Lead spawns N teammates via `Task` tool in a SINGLE message (per `Skill: dispatch-parallel`) — each gets IRON-RULE injection via PreToolUse:Task stderr.
4. Teammates claim tasks by ID (lowest unblocked first); set `owner` + `status=in_progress` via TaskUpdate.
5. Teammates work within file-ownership glob; cross-glob writes refused.
6. `Skill: team-coordinator` polls TaskList; synthesizes findings; resolves conflicts.
7. `Skill: refusal-discipline` for any teammate that can't complete its claim.
8. Stop-task hook blocks Stop if any teammate task still `in_progress`.

## Skills + agents

- `Task: shannon:team-builder` (lead/orchestrator)
- `Skill: team-coordinator` (TaskList synthesis)
- `Skill: dispatch-parallel` (single-message multi-Task pattern)
- `Skill: multi-agent-patterns` (charter-driven role definitions)
- Per teammate: whatever charter specifies — commonly `Task: shannon:executor`, `Task: shannon:validator`, `Task: shannon:reviewer`

## Success criteria

- All teammate tasks `completed`
- No orphan `in_progress` tasks
- Lead verdict written to `plans/reports/team-<run-id>.md`
- File-ownership violations: zero

## Examples

```
/shannon:team shannon-rebuild --charter team-charter.md --size 4
/shannon:team blog-audit --charter plans/audit-charter.md
```
