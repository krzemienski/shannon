# Contributing to Shannon

Shannon is a Claude Code plugin. Contributions land as PRs against this repo.

## What's expected

- **Iron Rule discipline** — see [docs/FUNCTIONAL_VALIDATION_GUIDE.md](FUNCTIONAL_VALIDATION_GUIDE.md). No mocks. No stubs. No `*.test.*` files. Validation evidence is real-system output cited specifically.
- **Doctor green** — `python3 scripts/doctor.py` must exit 0 with `mismatches: 0` after your change.
- **Harness green** — `bash scripts/harness/run-all.sh --dry-run` must exit 0.
- **No phantom references** — every `Skill: <name>` and `Task: <agent>` and `required_hooks: [name]` mention must resolve to a real v1 entity. The doctor checks the last; the Phase 3 resolution check covers the first two.

## Adding a skill

```bash
mkdir -p skills/<your-skill>/references
cat > skills/<your-skill>/SKILL.md <<'EOF'
---
name: <your-skill>
description: <one-line description with trigger phrases>
triggers:
  - "<trigger phrase 1>"
  - "<trigger phrase 2>"
required_hooks: []   # or list hooks if behavior depends on them
---

# <Your skill> skill

<body — explain when to use, what to do, examples>

## References

- See `references/foo.md` for <topic>
EOF
```

Add `references/<topic>.md` for any references the SKILL.md cites.

Verify:

```bash
python3 scripts/doctor.py    # mismatches: 0
```

## Adding an agent

```bash
mkdir -p agents/<your-agent>
cat > agents/<your-agent>/manifest.yml <<'EOF'
name: <your-agent>
description: "<role>"
priority: P1
embedded_skills:
  - <skill-1>
  - <skill-2>
related_standalone_skills:
  - <skill-3>
EOF

cat > agents/<your-agent>/AGENT.md <<'EOF'
---
name: <your-agent>
description: "<role>"
priority: P1
tools: "Read, Write, Skill"
embedded_skills_count: 2
---

# `<your-agent>` agent

<role description>

## Embedded skills

- **`<skill-1>`** — <why embedded>
- **`<skill-2>`** — <why embedded>

## Workflow

<TBD>

## Iron Rules

- No mocked evidence
- No fabricated PASS verdicts
- Refusal is a first-class outcome
EOF
```

Build + verify:

```bash
python3 build/embed-skills.py
python3 build/verify-build.py    # 0 mismatches
python3 scripts/doctor.py         # 0 mismatches
```

## Adding a command

```bash
cat > commands/<your-command>.md <<'EOF'
---
name: <your-command>
description: "<one-line>"
argument-hint: "<arg pattern>"
---

# /shannon:<your-command>

<body — describe behavior, modes, examples>

## Skills + agents

- `Skill: <skill-name>` (used for X)
- `Task: <agent-name>` (used for Y)

## Examples

\`\`\`
/shannon:<your-command> <example>
\`\`\`
EOF
```

Verify references resolve:

```bash
python3 scripts/doctor.py
```

(The doctor's "commands count" check will fire if you go below 13 or above 20.)

## Adding a hook

```javascript
// hooks/<your-hook>.js
// META
// name: <your-hook>
// event: <PreToolUse:X|PostToolUse:Y|...>
// consumed_by_skills: <skill-1>, <skill-2>
// description: <one-line>

const { runHook } = require('./_lib.js');

runHook('<your-hook>', (payload) => {
  // payload is the CC hook stdin JSON
  // return { decision: 'allow'|'block', exitCode: 0|2, stderrPayload: '...', stdoutPayload: '...' }
});
```

Register in `hooks/hooks.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "<your-event>",
        "hooks": [
          {"type": "command", "command": "PATH=\"/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH\" node \"${CLAUDE_PLUGIN_ROOT}/hooks/<your-hook>.js\""}
        ]
      }
    ]
  }
}
```

For every skill that depends on the new hook, add `required_hooks: [<your-hook>]` to its SKILL.md frontmatter.

Verify:

```bash
node -c hooks/<your-hook>.js     # syntax check
python3 scripts/doctor.py         # required_hooks contract
```

## Adding a benchmark

See [docs/DEV_HARNESS.md#adding-a-benchmark](DEV_HARNESS.md#adding-a-benchmark).

## Pre-PR checklist

- [ ] `python3 scripts/doctor.py` exits 0 with `mismatches: 0`
- [ ] `python3 build/verify-build.py` reports 0 mismatches
- [ ] `bash scripts/harness/run-all.sh --dry-run` exits 0
- [ ] No `*.test.*`, `*.spec.*`, `mock_*`, `stub_*` files anywhere in your diff (the harness scan will fail if found in `scripts/harness/`; manual review covers the rest)
- [ ] Updated relevant docs (SKILLS_CATALOG.md, ARCHITECTURE.md, README.md command table) if you added/removed/renamed skills/agents/commands/hooks
- [ ] If you added a new pillar (rare), updated BRIEF.md Section 4

## Style

- Markdown: GitHub-flavored. ATX-style headers (`#`). Code fences with language hint.
- Python: type hints where they clarify intent; not religious about it. Stdlib-first.
- JavaScript: vanilla Node, no transpilers, no external NPM deps for hook scripts.
- YAML: 2-space indent. Double-quote strings with embedded colons.

## License

Contributions are licensed under MIT, same as the project.

## Cross-references

- [README.md](../README.md) — overview
- [docs/ARCHITECTURE.md](ARCHITECTURE.md) — the layers
- [docs/FUNCTIONAL_VALIDATION_GUIDE.md](FUNCTIONAL_VALIDATION_GUIDE.md) — Iron Rule
- [docs/DEV_HARNESS.md](DEV_HARNESS.md) — running validation
- `.planning/ROADMAP.md` — phase plan
