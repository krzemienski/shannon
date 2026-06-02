---
name: scope
description: "Brownfield-aware discovery: parallel codebase analysis + skill/plugin inventory + proving-commands extraction. Read-only. Produces a scoping report that feeds /shannon:plan."
argument-hint: "[--repo <path>] [--task <description>] [--depth shallow|standard|deep]"
---

# /shannon:scope

The brownfield reconnaissance phase. Run this BEFORE `/shannon:plan` on any non-trivial existing codebase.

Read-only. No edits. Produces a scoping report citing what's actually on disk + what tools are available + what's the shortest path to "I can run this thing".

## Why this exists

Planning a brownfield change without first surveying the codebase + the available tooling is how plans end up referencing functions that don't exist, libraries that aren't installed, and skills that aren't loaded. `/shannon:scope` makes the brownfield context EXPLICIT and CITED before any plan synthesis runs.

## Inputs

- `--repo <path>` — defaults to current working directory
- `--task <description>` — what you're trying to do (refines the skill-inventory relevance scoring)
- `--depth shallow|standard|deep` — parallel sub-agent count for codebase-analysis (default `standard` = 5 scientists)

## Behavior

Three parallel streams via `Task: shannon:team-builder` using `Skill: dispatch-parallel` (single-message multi-Task):

### Stream 1 — `Skill: codebase-analysis` (5 parallel scientists)

| Scientist | Output |
|---|---|
| inventory | `evidence/<run-id>/codebase/file-inventory.txt` + `INVENTORY-FINDINGS.md` |
| deps | `evidence/<run-id>/codebase/deps-summary.md` |
| entry-points | `evidence/<run-id>/codebase/hot-paths.md` |
| proving-cmds | `evidence/<run-id>/codebase/proving-commands.json` |
| module-map | `evidence/<run-id>/codebase/module-map.md` |

### Stream 2 — `Skill: skill-inventory`

Walks the FILESYSTEM (no MCP) to enumerate skills: `~/.claude/skills/`, `<project>/.claude/skills/`, every plugin-root cache (hostloop + Application Support sessions + cowork plugins) with `.claude-plugin/plugin.json`. Cross-references `~/.claude/settings.json` `enabledPlugins` to filter to active-only. Writes `evidence/<run-id>/skills/skill-inventory.md` with directly relevant / tangentially relevant / unmatched tables, citing the exact SKILL.md path per entry. If `--task` was supplied, runs trigger + description-keyword relevance match; otherwise emits the full enumeration.

### Stream 3 — `Skill: observability-report`

Reads recent session JSONL (last 7 days by default) for prior decisions/lessons relevant to this repo. Writes `evidence/<run-id>/observability/session-context.md`.

### Stream 4 — `Skill: library-docs-fetch`

Reads `deps-summary.md` from Stream 1's output. For every third-party library, fetches authoritative docs via `llms.txt` probe → homepage docs → Context7 MCP → GitHub README (in that order). Writes `evidence/<run-id>/library-docs/<library-name>.md` per library + an `INDEX.md`. Refusals are written when no docs source succeeds — no training-data substitution.

After all four streams complete: `Task: shannon:planner` synthesizes a `scope-report.md` cross-citing the streams:

```markdown
# Scope report — <run-id>

## Codebase shape
[from Stream 1; cites specific files/lines]

## Available capabilities
[from Stream 2; cites specific skills + plugins from filesystem scan, with paths]

## Recent decisions affecting this work
[from Stream 3; cites specific session log lines]

## Third-party library API surface
[from Stream 4; one section per library with cited fetched-docs path; REFUSAL.md cited for any library that could not be fetched]

## Suggested planning approach
[concrete handoff to /shannon:plan with cited rationale grounded in all four streams]
```

## Skills + agents

- `Skill: codebase-analysis` (Stream 1 — code survey)
- `Skill: skill-inventory` (Stream 2 — filesystem-based skill discovery; no MCP)
- `Skill: observability-report` (Stream 3 — session-history context)
- `Skill: library-docs-fetch` (Stream 4 — third-party documentation fetch)
- `Skill: dispatch-parallel` (single-message orchestration)
- `Task: shannon:team-builder` (orchestrator)
- `Task: shannon:planner` (synthesis)

## Output

- `e2e-evidence/<run-id>/scope-report.md` — the synthesized handoff
- `e2e-evidence/<run-id>/codebase/` — codebase-analysis evidence (5 scientists)
- `e2e-evidence/<run-id>/skills/` — skill-inventory evidence (per-skill SKILL.md path table)
- `e2e-evidence/<run-id>/observability/` — observability evidence
- `e2e-evidence/<run-id>/library-docs/` — library-docs-fetch evidence (per-library .md or REFUSAL.md)

## Success criteria

- All three streams produced their evidence dirs
- `scope-report.md` cites specific files/skills/sessions (not generic claims)
- No edits made to source (verified by `git diff` empty at exit)
- Run-id'd so multiple scopes can coexist

## When to use

- Joining a project mid-stream and need orientation
- Planning a refactor or migration on existing code
- "What can Shannon + my installed plugins ACTUALLY do for this task?" — before spending tokens on planning
- Resuming work after a long pause (`/shannon:scope` re-grounds you)

## When NOT to use

- Greenfield project (no codebase to analyze)
- Trivial change you can describe in one sentence (just `/shannon:plan` or `/shannon:cook`)
- Already have a fresh scope report from the last hour (re-running wastes tokens)

## Examples

```
/shannon:scope --task "Add SSO with Okta to admin panel"
/shannon:scope --repo /path/to/repo --task "Migrate from REST to gRPC" --depth deep
/shannon:scope    # just inventory; no task — useful when joining a project
```
