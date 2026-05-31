# Shannon — BRIEF (v1 Vision)

> The single document that grounds every planning, design, and validation decision for Shannon v1. Per `anthropic-skills:create-validation-plan` discipline.

## Vision

A standalone Claude Code plugin that turns multi-stage agentic work into a sequence of provable steps. Users running Shannon get an opinionated methodology — Iron Rule validation, embedded sub-agent skills, single-message orchestration, meta-judge consensus — without giving up the flexibility Claude Code provides.

## The five pillars (architectural commitments)

1. **Embedded sub-agent skills** — Sub-agents at `agents/<name>/` carry their skills inline (after the build step). Spawning a sub-agent never fails because of a missing or shadowed skill.
2. **Orchestration** — Single-message multi-Task dispatch enforced by `team-builder` agent. Parallel / sequential / competitive patterns documented and validated.
3. **Iron Rule validation** — Every claim of completion cites real-system evidence captured to disk. Hooks refuse fabricated test files. No mocks.
4. **Meta-judge consensus** — `meta-judge` agent generates rubric YAML before any judge runs. Hidden thresholds. Debate on disagreement.
5. **Self-instrumented** — The plugin observes itself. `/shannon:doctor` reports hook ↔ skill contract health. `/shannon:audit` runs the skill-auditor sub-agent on demand.

## What v1 must do

| Capability | Acceptance criterion |
|---|---|
| Install as standalone plugin | `claude plugin install shannon` from a marketplace succeeds; no required MCP servers in the manifest |
| Function with zero MCPs | `claude plugin install shannon` followed by every documented workflow succeeds without Context7 / sequential-thinking installed |
| Function better with recommended MCPs | Same workflows demonstrably higher-quality (verified via benchmarks) when Context7 + sequential-thinking are present |
| Refuse to ship a verdict without evidence | Stop hook + completion-claim-validator hook + verification-before-completion skill all working in concert |
| Parallel sub-agent dispatch | I-01 benchmark passes (≥3 Task calls in one assistant message) |
| Meta-judge rubric primitive | I-03 benchmark passes (4-7 weighted dimensions summing to 1.0, hidden threshold) |
| Self-audit | `/shannon:audit` returns a structured report citing specific skills/agents/hooks/commands |
| Self-doctor | `/shannon:doctor` reports hook ↔ skill contract status |
| Embedded-skill loading | Spawning an agent via `Task(subagent_type=...)` succeeds even when the standalone `skills/<name>/SKILL.md` is removed (proves embedding works) |

## What v1 must NOT do

- Require a CLI install (`shannon` binary, `npx shannon`, etc.)
- Require any MCP server at install time
- Depend on any specific other plugin being installed
- Replace Claude Code as the runtime (Shannon runs inside it)
- Compete with IDEs (Cursor / Cline / Continue.dev) for the editor surface

## Component target shape (refined during Phase 1 audit)

- **Skills** (canonical source-of-truth): ~30 (curated from the 67 in `shannon-framework/skills/`)
- **Agents** (with embedded skill manifests): 8-12 (consolidated from 14)
- **Commands** (slash commands): 15-18 (reduced from 27 — remove duplicates and noise)
- **Hooks** (runtime enforcement): 6-8 (the load-bearing ones; consolidated from 14)
- **Core docs** (behavioral patterns): 5-7 (consolidated from 9)
- **User-facing docs**: 6 (README, INSTALL, QUICK_START, SKILLS_CATALOG, ARCHITECTURE, FUNCTIONAL_VALIDATION_GUIDE)
- **Dev docs**: 2 (CONTRIBUTING, DEV_HARNESS)

## Validation strategy

Two complementary harnesses, both required for every release candidate:

### 1. Agent SDK harness (`scripts/harness/sdk_runner.py`)
- Built on `claude-agent-sdk`
- Headless Python; fast iteration
- Per-pillar benchmarks; Iron Rule applied throughout
- Existing `run-validation.py` is the v7 starting point; v1 evolves it

### 2. Tmux harness (`scripts/harness/tmux_runner.py`)
- Spawns a real Claude Code terminal session inside a tmux pane
- Drives slash commands, captures rendered output
- Verifies: hook firing, slash command resolution, status line behavior, color codes, TTY-specific rendering
- **Full coverage** — every pillar gets ≥1 Tmux benchmark (not just self-instrumentation)

Both fail the release if they fail.

## Non-negotiables (the Iron Rule applied to Shannon's own development)

- v1 IS built using the same discipline it enforces on user work
- No mocks in the validation harnesses (real Claude Code sessions only)
- No test files (`test_*.py`, `*.test.ts`) anywhere in Shannon's source
- Every release ships with a functional-validation report; absence of the report blocks tagging

## Reference

Source documents that informed this BRIEF:
- `../docs/PRD-V1.md` (companion PRD with the architectural choices)
- `../docs/COMPETITIVE_ANALYSIS.md` (ecosystem positioning)
- `../docs/V7_FUNCTIONAL_VALIDATION.md` (proves standalone status is achievable)
- `../docs/SKILLS_CATALOG.md` (the 67-skill inventory to curate)
- `../docs/BENCHMARKS.md` (the 12 acceptance criteria evolved into v1 benchmarks)
- `../.v7/PROPOSED_ARCHITECTURE.md` (the 7-layer mental model)
- `DECISIONS.md` (the 5 user decisions that locked architecture C, MCP set, scope)

## Open assumptions (to be challenged during execution)

- **30 skills is the right reduction** — Phase 1 audit may discover that 35 or 25 is correct
- **Architecture C's build step is mechanical** — may discover edge cases that require additional logic
- **Tmux harness is feasible at full coverage** — may discover specific patterns that are SDK-only-testable
- **Context7 + sequential-thinking is the right MCP minimum** — research during Phase 1 may surface needs

Document deviations in the relevant phase's SUMMARY.md.
