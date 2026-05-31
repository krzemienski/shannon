---
name: retro
description: "Mine session JSONLs over N days; aggregate decisions, lessons, gotchas; write retrospective report."
argument-hint: "[--days N] [--scope project|session]"
---

# /shannon:retro

Sprint / weekly retrospective from session evidence. Every claim cites a session log.

## Inputs

- `--days N` (default 7)
- `--scope project|session` (default `project`)

## Behavior

1. Read session JSONLs from `~/.claude/projects/<project>/` for the last N days.
2. Extract decisions, lessons, gotchas, completed plans.
3. Group by week/day; aggregate metrics:
   - Tasks completed
   - Plans drafted vs executed
   - Failed approaches (count + categories)
   - Decisions made (with cite to session/turn)
4. Apply `Skill: reflect` per category — identify next experiment in PDCA (Plan/Do/Check/Act) form.
5. Output: `reports/retrospective-<date>.md`.

## Report structure

```markdown
# Retrospective — <date range>

## What shipped
- <list with PR / commit citations>

## What we learned
- <lesson> [source: session-<id>.jsonl turn N]

## What broke
- <gotcha> [source: ...]

## Decisions
- <decision> [source: ...]

## Next experiments (PDCA)
- Plan: <what to try>
- Do: <action>
- Check: <success criterion>
- Act: <integrate or revert>
```

## Skills + agents

- `Skill: observability-report` (session JSONL parsing + drift detection)
- `Skill: reflect` (per-category synthesis)
- `Skill: memorize` (save high-confidence lessons)

## Iron rules

- No invented lessons — every claim cites a session log line.
- No "we should do X" — propose PDCA experiments with measurable Check criterion.

## Examples

```
/shannon:retro
/shannon:retro --days 14 --scope project
```
