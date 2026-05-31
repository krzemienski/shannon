---
name: doctor
description: "Health check. Validates plugin manifest, hooks.json registration, settings.json sanity, log dirs writable, marketplace declarations, build state."
argument-hint: "[--verbose]"
---

# /shannon:doctor

Self-diagnostic. Reports installation health + drift.

## Inputs

- `--verbose` — include per-check details (default: summary only)

## Behavior

Runs these checks in order; emits PASS / FAIL per check:

1. **Plugin manifest** — `.claude-plugin/plugin.json` present, version valid, fields complete.
2. **Marketplace declaration** — `.claude-plugin/marketplace.json` present.
3. **Hooks registration** — `hooks/hooks.json` references scripts; all scripts present on disk.
4. **Settings.json sanity** — `~/.claude/settings.json` valid JSON; Shannon marketplace registered.
5. **Log dirs writable** — `~/.claude/logs/shannon/` exists and writable.
6. **CLI marketplace registration** — `/plugin list` includes `shannon@shannon-framework`.
7. **Build state** — `v1/shannon/agents/*/_built/skills/` populated and matches manifests (delegates to `build/verify-build.py`).
8. **Skills cascade** — every embedded skill's references/ resolve (delegates to verify-build).
9. **Required hooks contract** — every skill that declares `required_hooks:` has those hooks registered (Phase 4 work).

Output: stdout summary + `reports/doctor-<run-id>.md` with full details.

## Implementation

The command body delegates to `scripts/doctor.py`:

```bash
python3 scripts/doctor.py [--verbose]
```

That script reads the canonical sources (plugin.json, hooks.json, every skill's frontmatter, every agent's manifest, every agent's `_built/skills/` directory) and emits structured JSON to stdout. Exit code 0 on all-PASS; exit code 1 on any FAIL.

## Skills + agents

- `Skill: observability-report` (drift detection + dashboard formatting)
- `Skill: codebase-analysis` (manifest + settings inspection)

## Success criteria

- All checks PASS = healthy install.
- Any FAIL → actionable remediation message + path to relevant docs.

## Examples

```
/shannon:doctor
/shannon:doctor --verbose
```
