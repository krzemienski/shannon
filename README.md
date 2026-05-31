# Shannon

> Claude Code plugin for high-stakes multi-stage agentic work. Iron Rule: real-system evidence on disk, refuses verdicts without proof. Embedded sub-agent skills — sub-agents carry their skills, can't fail to load. Standalone — no required MCP servers.

**Version 1.0.0** — first stable release. The five pillars are on disk and self-verified by `/shannon:doctor`.

```bash
# In Claude Code — install from the GitHub repo:
/plugin marketplace add krzemienski/shannon
/plugin install shannon@shannon

# Or from a local clone:
/plugin marketplace add /path/to/shannon
/plugin install shannon@shannon-local
```

## What is this

A Claude Code plugin that turns multi-stage agentic work — research, planning, implementation, validation, release — into a sequence of provable steps.

Five pillars:

1. **Embedded sub-agent skills.** Sub-agents carry their skills inline; spawning is reliable.
2. **Orchestration.** Single-message multi-Task dispatch. Sequential, parallel, competitive patterns.
3. **Iron Rule validation.** Real-system evidence on disk. No mocks. No stubs. No test files.
4. **Meta-judge consensus.** Rubric YAML generated before any judge runs. Hidden thresholds. Debate on disagreement.
5. **Self-instrumented.** `/shannon:doctor` and `/shannon:audit` work — the plugin observes itself.

## What this is NOT

- Not a CLI tool. Plugin-only.
- Not an MCP framework. Uses MCP when present; degrades gracefully when absent.
- Not a replacement for Claude Code. Runs inside it.
- Not an IDE. Cursor/Cline/Continue.dev cover that surface.

## Recommended MCP servers

Optional but pair well:

- **Context7** — fresh library/API documentation
- **sequential-thinking** — systematic problem decomposition

Anything else: ship as research surfaces a need.

## Quick start

```bash
# 1. Install
# Local install (v0.1.x — marketplace publishing pending):
/plugin marketplace add /path/to/shannon-framework
/plugin install shannon@shannon-framework

# 2. Activate in your project
/shannon:enforce on

# 3. Verify
/shannon:doctor

# 4. First workflow
/shannon:plan "Your feature here"
/shannon:cook plans/<date>-<slug>/
```

Full guide: [docs/QUICK_START.md](docs/QUICK_START.md).

## The 20 commands

| Command | Purpose |
|---|---|
| `/shannon:plan` | Plan author (linear / brownfield / converge / tournament / deep) |
| `/shannon:scope` | Brownfield reconnaissance — codebase + skill inventory + session context |
| `/shannon:cook` | End-to-end execution with iron-rule validation |
| `/shannon:autopilot` | Refusal-driven retry loop around cook |
| `/shannon:fix` | 3-strike bug-fix runner |
| `/shannon:loop` | do/verify/reflect convergence loop |
| `/shannon:dispatch` | Sub-agent dispatch (sequential / parallel / competitive) |
| `/shannon:team` | Multi-teammate orchestration with file-ownership boundaries |
| `/shannon:validate` | Functional validation with cited evidence |
| `/shannon:audit` | Read-only audit (screen / app / session / drift / completion-evidence) |
| `/shannon:research` | Parallel researcher fan-out |
| `/shannon:prd` | Interview-driven PRD authoring |
| `/shannon:reflect` | Self-refinement (self / critique / memorize) |
| `/shannon:why` | Five-whys root-cause analysis |
| `/shannon:trace` | Session JSONL timeline |
| `/shannon:retro` | Mine sessions for retrospectives |
| `/shannon:resume` | Resume halted runs from evidence tree |
| `/shannon:enforce` | Toggle Shannon hooks (on/off) for current project |
| `/shannon:install` | Atomic install + activation |
| `/shannon:doctor` | Mechanical contract check |

## Architecture at a glance

Five layers:

1. **Skills (33)** — canonical at `skills/<name>/SKILL.md` + `references/*.md` (progressive disclosure)
2. **Agents (9)** — `agents/<name>/AGENT.md` with embedded SKILL.md content inlined by `build/embed-skills.py`
3. **Commands (20)** — `/shannon:*` entry points routing to agents/skills
4. **Hooks (7)** — `hooks/*.js` with `required_hooks` contract enforced by `scripts/doctor.py`
5. **Validation harnesses (2)** — `scripts/harness/sdk_runner.py` + `tmux_runner.py`

Full breakdown: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Status

**v1.0.0 — stable.** All five layers are on disk and pass the mechanical contract in
`scripts/doctor.py` (10/10 checks). The build path that produced v1 is preserved below as
provenance.

| Milestone | Status | Output |
|---|---|---|
| PRD approval | ✅ | PRD-V1.md + DECISIONS.md |
| Skill curation (67 → 33) | ✅ | `skills/` (33 dirs) |
| Agent embedding | ✅ | `agents/` (9 manifests + AGENT.md + `_built/`) |
| Command consolidation (27 → 20) | ✅ | `commands/` (20 dirs) |
| Hook curation (16 → 7) + contract | ✅ | `hooks/` (7) + `scripts/doctor.py` |
| Validation harnesses | ✅ | `scripts/harness/` (SDK + Tmux) |
| Documentation | ✅ | README + 7 docs/ files |
| Brownfield planning | ✅ | /shannon:scope + skill-inventory + --brownfield modes |
| v1.0.0 release | ✅ | doctor 10/10 PASS; counts reconciled to disk (33/9/20/7) |

## Provenance

Built on lessons from the v5/v6/v7 prototypes shipped in this repo and from Anthropic's ecosystem (anthropic-skills, claude-code-guide, sadd, oh-my-claudecode). The PRD-V1 reframe absorbed the productive ideas and dropped the rest.

## License

MIT.

## Documentation

- [docs/INSTALL.md](docs/INSTALL.md) — platform-specific install
- [docs/QUICK_START.md](docs/QUICK_START.md) — 10-minute path to first workflow
- [docs/SKILLS_CATALOG.md](docs/SKILLS_CATALOG.md) — the 33 skills
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 5 pillars + 5 layers + Architecture C internals
- [docs/FUNCTIONAL_VALIDATION_GUIDE.md](docs/FUNCTIONAL_VALIDATION_GUIDE.md) — Iron Rule + harness usage
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) — how to add a skill/agent/hook/command
- [docs/DEV_HARNESS.md](docs/DEV_HARNESS.md) — SDK + Tmux harness runbook
