# Shannon v1 — Developer harness guide

Two complementary harnesses validate Shannon end-to-end against real Claude Code:

1. **SDK harness** (`scripts/harness/sdk_runner.py`) — drives Shannon via the Python `claude_agent_sdk`. Programmatic; runs per-benchmark prompts; captures transcripts; emits structured verdicts.
2. **Tmux harness** (`scripts/harness/tmux_runner.py`) — drives Shannon via `claude` CLI inside a tmux pane. Simulates a real user typing slash commands; captures pane output; emits verdicts.

Both target the same 5 pillars and the same benchmark specs. Two implementations exist because they catch different failure modes (SDK exposes the API surface; Tmux exposes the CLI integration surface).

## Quick start

```bash
# Validate the harness loads + the benchmark coverage looks right.
bash scripts/harness/run-all.sh --dry-run

# Run live (requires Claude API key + Claude Code CLI installed).
export ANTHROPIC_API_KEY=sk-ant-...
bash scripts/harness/run-all.sh --live
```

The dry-run is the structural check used by Phase 5's gate. The live run is the runtime check used by Phase 7 (release-candidate verification).

## Files

| File | Purpose |
|---|---|
| `scripts/harness/lib.py` | Shared utilities: benchmark loader, validator, Verdict dataclass, evidence writer |
| `scripts/harness/sdk_runner.py` | SDK harness (Python `claude_agent_sdk`) |
| `scripts/harness/tmux_runner.py` | Tmux harness (spawns `claude` CLI) |
| `scripts/harness/run-all.sh` | Orchestrator — runs both, aggregates exit codes |
| `scripts/harness/benchmarks/*.yml` | Per-pillar benchmark specs |

## Modes

### `--dry-run`

- Loads every benchmark YAML
- Validates structure (id, pillar, goal, action, gate_criteria all present)
- Reports pillar coverage
- Probes tooling (tmux + claude availability)
- Emits `DRY_RUN_OK` per valid benchmark, `FAIL` per invalid spec
- Exits 0 if all benchmarks are valid; 1 otherwise

`--dry-run` NEVER reports `PASS` for actual benchmark execution. A `DRY_RUN_OK` means "the spec is valid and ready for `--live` execution", nothing more.

### `--live`

- Requires `ANTHROPIC_API_KEY` set
- For SDK: requires `pip install claude-agent-sdk`
- For Tmux: requires `tmux` and `claude` CLI on PATH
- Spawns the relevant runtime per benchmark
- Captures transcript / pane output to `.planning/phases/05-harnesses/evidence/<benchmark-id>/`
- Emits `PASS` or `FAIL` per benchmark with cited evidence path
- Exits 0 only if at least one benchmark `PASS`ed

If the live environment is incomplete (no SDK installed, no tmux, no API key), the runner emits explicit `SKIP` verdicts with remediation steps and exits 1 — never fabricates `PASS`.

## The 5 pillar benchmarks

| File | Pillar | What it proves |
|---|---|---|
| `pillar-01-embedded-skills.yml` | Embedded sub-agent skills (Architecture C) | meta-judge spawn includes inlined judge SKILL.md content |
| `pillar-02-orchestration.yml` | Orchestration | `/shannon:dispatch --mode parallel` does single-message multi-Task spawn |
| `pillar-03-iron-rule.yml` | Iron Rule | `block-fab-files` hook refuses `tests/*.test.js` Write with exit 2 |
| `pillar-04-meta-judge.yml` | Meta-judge consensus | rubric YAML appears in transcript BEFORE any judging verdict |
| `pillar-05-self-instrumented.yml` | Self-instrumented | `scripts/doctor.py` exits 0; `summary.mismatches == 0` |

## Adding a benchmark

```yaml
# scripts/harness/benchmarks/<your-name>.yml
id: <unique-id>
pillar: <one-of-the-5-pillars>
goal: <one-sentence-what-this-proves>
setup:
  - <bash command 1>
  - <bash command 2>
action:
  type: <slash-command | spawn-subagent | tool-call | shell | pipeline>
  # ... action-specific fields
expected_evidence:
  - <human-readable evidence item 1>
  - <human-readable evidence item 2>
gate_criteria:
  - <machine-verifiable gate 1>
  - <machine-verifiable gate 2>
runner: both  # sdk | tmux | both
```

Then:

```bash
# Verify your benchmark parses + validates
bash scripts/harness/run-all.sh --dry-run
```

If your benchmark targets a new pillar, also update `BRIEF.md` Section 4 (Pillars).

## Iron Rule

The harness does NOT contain:

- `test_*.py`, `*_test.py`, `*.test.*`, `*.spec.*` files
- `mock_*`, `stub_*`, `fixture_*` modules
- Conditional code that fabricates `PASS` when the real check can't run

All "would have tested" outcomes show as `SKIP` with explicit remediation. The validation gate refuses to ship if any verdict is fabricated.

## Sandbox vs target environment

The Phase 5 validation in `.planning/phases/05-harnesses/PHASE-05-VALIDATION.md` reflects structural completeness: the harness exists, parses benchmarks, validates them, and exits 0 in `--dry-run` mode from the sandbox where the build was done.

The live runtime check is the user-action validation captured in Phase 7 (release-candidate run on a target machine with Claude API access). DEV_HARNESS.md provides the runbook for that.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `claude_agent_sdk not installed` in --live | SDK not pip-installed | `pip install claude-agent-sdk` |
| `tmux not installed` in --live | Tmux not on PATH | `brew install tmux` (macOS) / `apt-get install tmux` (Linux) |
| `claude CLI not installed` in --live | Claude Code not installed | Install from anthropic.com |
| dry-run reports `invalid_specs` | One or more benchmark YAML missing fields | Check the validator output; add missing field |
| run-all.sh exits 1 in --dry-run | A runner reported invalid spec OR a Python import failed | Check `evidence/sdk-dry-run.json` and `evidence/tmux-dry-run.json` for details |

## Contributing

When adding a new pillar (rare): update BRIEF.md Section 4, add a benchmark YAML, and document the new pillar in this file.

When adding a benchmark to an existing pillar: just drop a new YAML in `benchmarks/`. The harness auto-discovers via `lib.load_benchmarks()`.

When changing harness code: keep the Iron Rule. The CI gate refuses to ship if the harness directory contains forbidden file patterns.
