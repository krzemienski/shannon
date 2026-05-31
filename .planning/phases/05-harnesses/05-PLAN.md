# Plan 05: SDK + Tmux validation harnesses (5 pillars × ≥1 benchmark each)

> **This PLAN.md is the execution prompt.** Same combined-plan pattern as Phases 3 and 4.

---

## Prerequisite check (BLOCKING)

```bash
test -f ../04-hooks/PHASE-04-VALIDATION.md
grep -qE 'Verdict.*PASS' ../04-hooks/PHASE-04-VALIDATION.md
python3 ../../../scripts/doctor.py | python3 -c "import json,sys; assert json.load(sys.stdin)['summary']['mismatches']==0"
```

---

## Mock detection preamble

REFUSED tasks:

- Writing a "harness" that contains `mock_*`, `stub_*`, `*.test.*`, `*.spec.*`, or `test_*.py` files.
- Producing a `--dry-run` mode that fabricates PASS verdicts (it must report structurally what would happen, not "it passed").
- Skipping the benchmark-coverage check (≥1 benchmark per pillar = 5 total minimum).
- Writing harness code that imports a Claude Agent SDK class that doesn't exist (phantom API).

---

## Context

- **Phase**: 5 (Validation harnesses)
- **Predecessor**: Phase 4 PASS (7 hooks; required_hooks contract enforced; doctor.py 0 mismatches)
- **Goal**: build BOTH harnesses to full coverage of the 5 pillars per user's "full Tmux coverage" decision (D4)
- **Inputs**:
  - 5 pillars from `BRIEF.md`
  - 9 v1 agents + 31 v1 skills + 19 v1 commands + 7 v1 hooks
  - Working `build/embed-skills.py` + `scripts/doctor.py`
- **Outputs**:
  - `scripts/harness/sdk_runner.py` — Claude Agent SDK driver
  - `scripts/harness/tmux_runner.py` — Tmux-based Claude Code driver
  - `scripts/harness/lib.py` — shared utilities
  - `scripts/harness/benchmarks/<pillar>.yml` — 5+ benchmark specs (one per pillar minimum)
  - `scripts/harness/run-all.sh` — orchestrator that dispatches both harnesses
  - `docs/DEV_HARNESS.md` — contributor doc
  - `PHASE-05-VALIDATION.md`

## 5 pillars (from BRIEF)

| # | Pillar | Benchmark target |
|---|---|---|
| 1 | Embedded sub-agent skills (Architecture C) | Spawn `meta-judge`; verify response cites embedded `judge` content from AGENT.md |
| 2 | Orchestration (parallel dispatch) | Run `/shannon:dispatch --mode parallel` with 2 tasks; verify single-message multi-Task pattern in transcript |
| 3 | Iron Rule validation (functional-validation + no-fakes-discipline) | Attempt `Write tests/foo.test.js`; verify `block-fab-files` hook refuses with exit 2 |
| 4 | Meta-judge consensus (rubric YAML before judge) | Invoke `meta-judge` → `judge` pipeline; verify rubric YAML appears in transcript BEFORE any judging verdict |
| 5 | Self-instrumented (doctor + hooks) | Run `/shannon:doctor`; verify exit 0 + summary.mismatches == 0 |

## Tasks

### Task 1 — Write `scripts/harness/lib.py` (shared utilities)

Functions:
- `load_benchmarks() -> list[BenchmarkSpec]` — reads `benchmarks/*.yml`
- `validate_benchmark(spec) -> list[str]` — returns issues; empty list = valid
- `Verdict(name, status, evidence_path, detail)` dataclass
- `write_evidence(path, content)` — writes to `.planning/phases/05-harnesses/evidence/<path>`

### Task 2 — Write `scripts/harness/sdk_runner.py`

- `--dry-run` (default): load benchmarks, validate, print structured report, exit 0
- `--live`: import `claude_agent_sdk`, invoke per-benchmark interaction, capture transcript, emit verdict
- `--benchmark <name>`: run just that benchmark
- Iron Rule: live mode requires real API access; dry-run mode CANNOT fabricate verdicts.

### Task 3 — Write `scripts/harness/tmux_runner.py`

- `--dry-run`: list benchmarks + check tmux/claude-code availability
- `--live`: spawn `claude code` in a tmux pane; send slash commands; capture pane output; emit verdict
- Same Iron Rule.

### Task 4 — Write `scripts/harness/benchmarks/<pillar>.yml` (5 files)

One per pillar per the table above. Each spec includes:
- `id`, `pillar`, `goal`, `setup`, `action`, `expected_evidence`, `gate_criteria`

### Task 5 — Write `scripts/harness/run-all.sh`

- `--dry-run` (default): run both sdk_runner --dry-run + tmux_runner --dry-run; print aggregate report; exit 0 if both dry-runs exit 0
- `--sdk` / `--tmux` / `--all`: select runner(s)
- `--live`: pass through to runners
- Iron Rule: this script must NOT silently substitute --dry-run for --live when API isn't available; --live failures are explicit.

### Task 6 — Write `docs/DEV_HARNESS.md`

Contributor doc per ROADMAP Phase 5. Covers:
- How to run harnesses locally
- How to add a benchmark
- Dry-run vs Live mode
- Iron Rule discipline (why no `test_*` files)

## Phase-level regression check

```bash
# Phase 0+1+2+3+4
test -f ../../BRIEF.md && test -f ../../ROADMAP.md
test -f ../01-curation/PHASE-01-VALIDATION.md && [ $(ls ../../../skills/ | wc -l) -eq 31 ]
test -f ../02-agent-embedding/PHASE-02-VALIDATION.md && [ $(ls ../../../agents/ | wc -l) -eq 9 ]
test -f ../03-commands/PHASE-03-VALIDATION.md && [ $(ls ../../../commands/ | wc -l) -ge 13 ]
test -f ../04-hooks/PHASE-04-VALIDATION.md
python3 ../../../scripts/doctor.py | python3 -c "import json,sys; assert json.load(sys.stdin)['summary']['mismatches']==0"
```

## Plan gate (BLOCKING)

Phase 5 PASSes when:

1. ✅ `sdk_runner.py`, `tmux_runner.py`, `lib.py`, `run-all.sh` all exist and are syntax-valid
2. ✅ ≥5 benchmarks in `benchmarks/` covering all 5 pillars
3. ✅ `python3 sdk_runner.py --dry-run` exits 0; reports benchmark coverage
4. ✅ `python3 tmux_runner.py --dry-run` exits 0; reports availability
5. ✅ `bash run-all.sh --dry-run` exits 0; reports both runners' dry-runs
6. ✅ Iron Rule scan: 0 occurrences of `test_*.py`, `*.test.*`, `mock_*`, `stub_*` in `scripts/harness/`
7. ✅ `docs/DEV_HARNESS.md` exists
8. ✅ Phase 0+1+2+3+4 regression PASS (doctor.py 0 mismatches)

## Honest scoping

The sandbox cannot reach the live Claude API. Therefore:

- `--dry-run` mode is the structural-completeness check (Phase 5 gate).
- `--live` mode is the runtime-correctness check (user-action, run on a machine with Claude API access).
- The Phase 5 PASS verdict reflects structural completeness; live runtime validation is a documented user action in DEV_HARNESS.md.

This is the same scoping pattern used in Plan 02-03 (Architecture C structural proof vs runtime proof).

## Done condition

`PHASE-05-VALIDATION.md` with verdict=PASS. Phase 6 (Documentation) unblocked.

## Iron Rule restatement

- No `test_*.py`, `*.test.*`, `mock_*`, `stub_*` files anywhere in `scripts/harness/`.
- `--dry-run` does NOT report PASS for what would have been tested; it reports COVERAGE of what the harness can execute.
- Benchmark YAMLs reference REAL v1 agents/skills/commands/hooks — no phantoms.
