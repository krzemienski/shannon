# Installation

Shannon is a Claude Code plugin. Installation is via the Claude Code plugin marketplace.

## Requirements

- **Claude Code** ≥ 6.0 (the version with plugin support)
- **Python 3.10+** (for `build/embed-skills.py`, `scripts/doctor.py`, `scripts/harness/*`)
- **Node 18+** (for hook scripts)
- **PyYAML** (`pip install pyyaml`)

Optional but recommended:
- **tmux** — for the Tmux validation harness
- **Context7 MCP** — for fresh library docs
- **sequential-thinking MCP** — for systematic problem decomposition

## Standard install (when published to marketplace)

```bash
# In Claude Code:
# When marketplace publishing lands (v0.2+):
# /plugin marketplace add krzemienski/shannon
# For v0.1.x, use local install (see Local install section)
/plugin install shannon
```

Restart Claude Code, then activate in your project:

```bash
/shannon:enforce on
/shannon:doctor    # should report 0 mismatches
```

## Local install (during v0.x development)

If you have this repo checked out locally:

```bash
# In Claude Code:
/plugin marketplace add /path/to/shannon-framework
/plugin install shannon@shannon-framework

# Restart Claude Code
/shannon:enforce on
/shannon:doctor
```

## Build step (one-time, after install)

Architecture C requires building the embedded-skills payload:

```bash
cd <plugin-root>/v1/shannon
python3 build/embed-skills.py
python3 build/verify-build.py    # should report 0 mismatches
```

This populates `agents/<name>/_built/skills/` for every agent's manifest. Re-run any time you change a skill or a manifest.

## Verify install

```bash
python3 scripts/doctor.py
```

Expect output ending in:

```json
"summary": {
  "checks_pass": 8,
  "checks_fail": 0,
  "mismatches": 0
}
```

Any FAIL needs to be resolved before relying on Shannon for real work.

## Conflicting plugins

Shannon absorbs ideas from several other plugins (sadd, oh-my-claudecode, validationforge, crucible, deepest-plan, ralph-loop, anneal-*, lynx, ck, planning-with-files, retrospective-analyzer). If those are also installed, you may see overlapping commands. Choose one:

- **Replace mode**: `/shannon:install --replace` prompts before disabling the overlapping plugins.
- **Parallel mode**: `/shannon:install --parallel` skips the disable step (you manage conflicts manually).

## Uninstall

```bash
# In Claude Code:
/plugin uninstall shannon@shannon-framework
```

Optionally remove the per-project sentinel:

```bash
rm -rf .shannon/
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `/shannon:doctor` reports `hooks count not in [5,9]` | Hook files missing — re-install the plugin |
| `/shannon:doctor` reports `required_hooks → registered hooks` FAIL | One or more `required_hooks` declarations in skill frontmatter reference unregistered hooks — check `hooks/hooks.json` |
| `/shannon:doctor` reports `Agents _built/ matches manifest` FAIL | Re-run `python3 build/embed-skills.py` |
| Hooks not firing in my project | Did you run `/shannon:enforce on`? Hooks no-op by default in projects without `.shannon/active` |
| Hooks firing in unrelated projects | `/shannon:enforce off` in that project; or set `SHANNON_DISABLE=1` in shell to disable globally |

## Cross-references

- [README.md](../README.md) — overview
- [docs/QUICK_START.md](QUICK_START.md) — first workflow
- [docs/ARCHITECTURE.md](ARCHITECTURE.md) — internals
- [docs/DEV_HARNESS.md](DEV_HARNESS.md) — running harnesses locally
