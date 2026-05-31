---
name: install
description: "Idempotent setup. Marketplace declaration → install Shannon plugin → optionally disable conflicting plugins → verify via /shannon:doctor."
argument-hint: "[--parallel | --replace]"
---

# /shannon:install

Atomic install + activation.

## Inputs

- `--parallel` — coexist with other plugins (skip conflict-disable step)
- `--replace` — default; prompts before disabling conflicting plugins

## Behavior

1. **Verify plugin tree** — confirm Shannon files present in current marketplace path. Run schema validation against `.claude-plugin/plugin.json`.
2. **Marketplace declaration** — read `~/.claude/settings.json`. If Shannon marketplace not declared, add it.
3. **Install** — run `/plugin install shannon@shannon-framework` (or provide manual instruction).
4. **Replace mode (default)** — list conflicting plugins (e.g., other planning/validation plugins); y/N prompt; on `y`, set `enabledPlugins["<slug>"] = false` for each; print diff; tell user to restart Claude Code.
5. **Parallel mode** — skip step 4.
6. **Build** — run `python3 build/embed-skills.py` to populate `agents/*/_built/skills/`.
7. **Verify** — invoke `/shannon:doctor`; require all checks PASS.

## Skills + agents

- `Skill: observability-report` (for doctor verification)
- `Skill: codebase-analysis` (manifest inspection)
- `Skill: python-agent-sdk` (harness reference — points users to the SDK contract for downstream automation)

## Success criteria

- Marketplace declared.
- Shannon plugin installed (visible in `/plugin list`).
- Conflicting plugins disabled (`--replace` mode).
- Build run successful.
- `/shannon:doctor` all green.

## Examples

```
/shannon:install
/shannon:install --parallel    # coexist mode
```
