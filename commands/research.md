---
name: research
description: "Parallel researcher fan-out; aggregator writes cited research summary."
argument-hint: "<topic> [--sources N] [--depth shallow|standard|deep]"
---

# /shannon:research

Topic research with parallel sub-agent fan-out. Standalone command (not a subcommand of plan).

## Inputs

- Positional: research topic
- `--sources N` — minimum sources required (default 5)
- `--depth shallow|standard|deep` (default `standard`)

## Behavior

1. Decompose topic into sub-topics (3-5 typically) via `Skill: codebase-analysis` (decomposition mode).
2. Spawn parallel sub-agents via `Task: team-builder` (orchestrator). team-builder uses `Skill: dispatch-parallel` to spawn N `Task: executor` workers in a single message — one per sub-topic.
3. Each worker:
   - Uses `WebFetch` and `context7` MCP for primary sources.
   - Writes findings to `research/<topic-slug>/researcher-<N>.md` with inline citations.
4. After workers complete, `Task: planner` reads all reports; writes `research/<topic-slug>/SUMMARY.md` synthesizing findings with cross-citations.

## Skills + agents

- `Task: team-builder` (parallel dispatch orchestrator)
- `Task: executor` (research workers)
- `Task: planner` (synthesis)
- `Skill: dispatch-parallel`
- `Skill: codebase-analysis` (decomposition)
- `Skill: plan-author` (synthesis)

## Iron rules

- Citations always specific (URL + retrieval timestamp).
- No "according to my training data" — refuse, fetch live.

## Examples

```
/shannon:research "OAuth2 PKCE best practices 2025"
/shannon:research "Postgres logical replication for blue-green deploys" --depth deep
```
