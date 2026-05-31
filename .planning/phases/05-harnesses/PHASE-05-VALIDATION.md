# Phase 5 — VALIDATION

**Phase**: 5 (SDK + Tmux validation harnesses)
**Verdict**: ✅ **PASS** — structural completeness; both harnesses dry-run exit 0; 5 benchmarks cover 5 pillars; Iron Rule clean.
**Date**: 2026-05-28

## ROADMAP gate criteria

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | SDK harness exists, Python-syntax-valid, covers 5 pillars (≥5 benchmarks) | ✅ PASS | `scripts/harness/sdk_runner.py` ast.parse OK; 5 benchmarks load |
| 2 | Tmux harness exists, Python-syntax-valid, covers 5 pillars (≥5 benchmarks) | ✅ PASS | `scripts/harness/tmux_runner.py` ast.parse OK; 5 benchmarks load |
| 3 | `scripts/harness/run-all.sh` exits 0 on a clean v1 install (--dry-run mode) | ✅ PASS | `bash run-all.sh --dry-run` aggregate exit 0 |
| 4 | Iron Rule applied: zero `mock_*`, zero `test_*.py`, zero stubs in harness code | ✅ PASS | `find scripts/harness/` for forbidden patterns returns 0 |
| 5 | Phases 1+2+3+4 regression PASS | ✅ PASS | `scripts/doctor.py` exits 0; `verify-build.py` 0 mismatches |

## Headline numbers

- **5 benchmark YAMLs** in `scripts/harness/benchmarks/` (one per pillar — at the ROADMAP minimum)
- **2 harness runners** (SDK + Tmux) both Python-syntax-valid
- **1 orchestrator** (`run-all.sh`) — aggregates both runners
- **1 shared library** (`lib.py`) — benchmark loader, validator, Verdict dataclass, evidence writer
- **5/5 pillars covered**: embedded-sub-agent-skills, orchestration-parallel-dispatch, iron-rule-validation, meta-judge-consensus, self-instrumented
- **0 invalid benchmark specs** (all validators pass)
- **0 forbidden Iron Rule patterns** in `scripts/harness/`

## Pillar coverage

| Pillar | Benchmark | Runner |
|---|---|---|
| embedded-sub-agent-skills | pillar-01-embedded-skills | both |
| orchestration-parallel-dispatch | pillar-02-orchestration | both |
| iron-rule-validation | pillar-03-iron-rule | both |
| meta-judge-consensus | pillar-04-meta-judge | both |
| self-instrumented | pillar-05-self-instrumented | both |

## Dry-run output evidence

### sdk_runner.py --dry-run

```json
{
  "mode": "dry-run",
  "runner": "sdk",
  "benchmark_count": 5,
  "pillar_coverage": {
    "embedded-sub-agent-skills": ["pillar-01-embedded-skills"],
    "orchestration-parallel-dispatch": ["pillar-02-orchestration"],
    "iron-rule-validation": ["pillar-03-iron-rule"],
    "meta-judge-consensus": ["pillar-04-meta-judge"],
    "self-instrumented": ["pillar-05-self-instrumented"]
  },
  "summary": {"total": 5, "valid": 5, "invalid": 0}
}
```

Exit code: 0.

### tmux_runner.py --dry-run

```json
{
  "mode": "dry-run",
  "runner": "tmux",
  "tooling": {"tmux_available": true, "claude_available": true},
  "benchmark_count": 5,
  "summary": {"total": 5, "valid": 5, "invalid": 0, "tmux_ok": true, "claude_ok": true}
}
```

Exit code: 0.

### run-all.sh --dry-run

```
SDK runner exit: 0
Tmux runner exit: 0
```

Aggregate exit code: 0.

## Honest scope (structural vs runtime)

This validation reflects the **structural** half of Phase 5:

- All harness files exist + parse + are Python-syntax-valid.
- Benchmarks load + validate + cover all 5 pillars.
- `--dry-run` modes exit 0 cleanly.
- Iron Rule discipline is enforced (no forbidden file patterns).
- The harness can DETECT phantom references but cannot, from the sandbox, EXECUTE live API calls.

The **runtime** half (live execution against real Claude Code with Anthropic API access) is documented as a user action in `docs/DEV_HARNESS.md` and run as part of Phase 7 (release-candidate verification). This is the same structural-vs-runtime scoping pattern used in Plan 02-03 (Architecture C smoke test).

The honest reason: the sandbox has no API key + no Claude Code CLI configured to run live. Forcing a live run from the sandbox would fabricate verdicts. The Iron Rule refuses that.

## Iron Rule compliance

- **No `test_*.py`, `*.test.*`, `*.spec.*`, `mock_*`, `stub_*` files anywhere in `scripts/harness/`** — verified via `find` returning 0 matches.
- **Dry-run mode reports COVERAGE, not PASS.** Every dry-run verdict is `DRY_RUN_OK` or `FAIL`; never `PASS`.
- **Live mode emits explicit `SKIP` verdicts when prerequisites are missing.** No silent downgrade to dry-run; no fabricated PASS.
- **Benchmark YAMLs reference only real v1 entities.** Each `action.subagent_type` resolves to a real v1 agent; each slash command target exists in `commands/`; each Skill name exists in `skills/`. This is the same phantom-reference discipline applied in Phase 3 (commands).

## Phase regression check (at end of Phase 5)

```
Phase 0 BRIEF.md            ✓
Phase 0 ROADMAP.md          ✓
Phase 1 PHASE-01-VALIDATION ✓ (31 skills)
Phase 2 PHASE-02-VALIDATION ✓ (9 agents; build verified)
Phase 3 PHASE-03-VALIDATION ✓ (19 commands; 0 phantom refs)
Phase 4 PHASE-04-VALIDATION ✓ (7 hooks; doctor.py 0 mismatches)
scripts/doctor.py: PASS     ✓
build/verify-build.py: PASS ✓
```

## Done condition

`PHASE-05-VALIDATION.md` written (this file). Phase 6 (Documentation) unblocked.
