---
name: reflect
description: "Self-refinement pass. Modes: self | critique | memorize."
argument-hint: "[--mode self|critique|memorize] [--target <session-or-pr>]"
---

# /shannon:reflect

Self-refinement loop. Three modes; pick one per invocation.

## Inputs

- `--mode self|critique|memorize` (default `self`)
- `--target <session-id-or-PR-number>` — for `critique`/`memorize`; optional for `self`

## Behavior

### --mode self
1. Read the last assistant turn in the current session.
2. Identify gaps (unaddressed asks, vague claims, missing evidence).
3. Propose specific fixes.
4. Output: `reflect.md` at current location.

### --mode critique
1. Spawn `Task: shannon:critic` in isolated context against target artifact.
2. Critic emits findings BLOCKING/HIGH/MEDIUM/LOW with cited file:line.
3. Output: `critique.md`.

### --mode memorize
1. Extract a learned pattern from the current session or target.
2. Save to `~/.claude/memory/` (or project-local) with structured frontmatter (name slug, type, description).
3. Cross-link via `[[name]]` to related memories.
4. Update MEMORY.md index.

## Skills + agents

- `Skill: reflect` (self mode)
- `Skill: judge` (critique mode — used by critic)
- `Skill: memorize` (memorize mode)
- `Task: shannon:critic` (critique mode)

## Success criteria

- Mode-specific output written.
- For `critique`: every finding cites a path.
- For `memorize`: memory entry has frontmatter + MEMORY.md index updated.

## Examples

```
/shannon:reflect
/shannon:reflect --mode critique --target plans/260528-feature-x/plan.md
/shannon:reflect --mode memorize --target current-session
```
