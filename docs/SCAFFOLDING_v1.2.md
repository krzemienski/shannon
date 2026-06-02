# Shannon v1.2.0 — Scaffolding Guide

How to add the four component types, kept separate from implementation internals. The contract each must satisfy is enforced by `scripts/doctor.py` + the Phase-3 resolution check. After any add: `python3 scripts/doctor.py` must exit 0 with `mismatches: 0`.

## Conventions (all four types)

- **Naming:** kebab-case dirs/files. A skill/agent's `name:` frontmatter MUST equal its directory/file basename (doctor enforces agent name==file).
- **Frontmatter first line is `---`.** Skills + agents require `name` + `description`; skills add `triggers:`; agents add `tools:` + `skills:`.
- **No phantom references.** Every `Skill: <name>`, `Task: <agent>`, `required_hooks: [<name>]`, and agent `skills:` entry must resolve to a real on-disk entity.
- **Iron Rule.** No `*.test.*`, mock, or stub files — `block-fab-files` hook rejects them at write time.

## Add a command — `commands/<name>.md`

```markdown
---
name: <name>
description: <one line; what it does + when to invoke>
argument-hint: "<args>"
---
# /shannon:<name>
## Behavior
Numbered phases; each cites the Skill/Agent it invokes.
## Skills invoked
- `<skill>`  (must exist in skills/)
```
Doctor count range: 13-24.

## Add a skill — `skills/<name>/SKILL.md`

```markdown
---
name: <name>
description: <ALWAYS use when ... directive, trigger-forward>
triggers:
  - "phrase a"
  - "phrase b"
---
# <name>
## Behavior contract
## When to use / When NOT to use
## Iron rules
```
- `references/` subfiles allowed (progressive disclosure); reference them by relative path.
- Trigger-less skills score `f1=0, benched=false` in skills10x — only add a skill without triggers if it is invoked structurally (by an agent/command), never expected to self-activate.
- Doctor count range: 25-40.

## Add an agent — `agents/<name>.md`

```markdown
---
name: <name>
description: "<role>"
priority: P1
tools: "Read, Grep, Glob, Skill"
skills: skill-a, skill-b
---
# `<name>` agent
## Responsibilities
## Constraints (Iron Rule)
## Inherited skills (all must resolve)
```
- Every name in `skills:` MUST have a `skills/<that>/SKILL.md`. This is native skill inheritance (D8) — the agent loads them at spawn; it cannot silently fail to load.
- Include `Skill` in `tools:` if the agent invokes skills at runtime.
- Doctor count range: 5-12.

## Add a hook — `hooks/<name>.js` + register in `hooks/hooks.json`

- Follow the existing hook output protocol (see a sibling hook + `_lib.js`). PreToolUse block = stderr + exit 2; PostToolUse feedback = stderr + exit 2; allow = silent exit 0; context inject = stdout exit 0.
- Register the matcher + event in `hooks/hooks.json` (doctor validates the JSON + that each script exists and is executable).

## The three harnesses (don't confuse them)

`scripts/harness/` holds three distinct validation harnesses — all real-session, no mocks:

| Harness | Files | Proves |
|---|---|---|
| SDK pillars | `sdk_runner.py`, `run-all.sh` | 5 pillars via `claude_agent_sdk` |
| Tmux pillars | `tmux_runner.py` | 5 pillars via `claude` CLI in tmux |
| Activation gate (v1.2, G1) | `drive-tests.sh`, `drive-tests-csd.sh` | opt-in skill-activation gate fires correctly per fixture |

Plus `scripts/skills10x/` — the self-improve grading+improvement loop (separate from validation; it *edits* skills, the harnesses only *verify*).

## Verification after any scaffold

```bash
python3 scripts/doctor.py          # exit 0, mismatches: 0
bash scripts/harness/run-all.sh --dry-run   # exit 0
```
