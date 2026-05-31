# Phase 5 Summary — SDK + Tmux validation harnesses (5 pillars × ≥1 benchmark each)

**Outputs**:
- `scripts/harness/sdk_runner.py` — Claude Agent SDK runner
- `scripts/harness/tmux_runner.py` — Tmux/Claude-CLI runner
- `scripts/harness/lib.py` — shared library
- `scripts/harness/benchmarks/*.yml` — 5 benchmark specs
- `scripts/harness/run-all.sh` — orchestrator
- `docs/DEV_HARNESS.md` — contributor doc
- `PHASE-05-VALIDATION.md`

## Headline

- **5 benchmarks** covering all 5 pillars (1:1)
- **Both runners** dry-run exit 0
- **run-all.sh** orchestrator dry-run exits 0
- **0 forbidden Iron Rule patterns** in harness code
- **All entities referenced in benchmarks resolve** to real v1 skills/agents/commands/hooks (doctor.py-style contract check)

## Honest scoping

Phase 5's PASS is **structural**: harness exists, dry-run runs end-to-end, Iron Rule clean. The **runtime** PASS (real API + real Claude Code session) is a user action documented in DEV_HARNESS.md and run as part of Phase 7 (release-candidate verification).

This is the same structural-vs-runtime split used in Plan 02-03 for Architecture C — the sandbox can't reach the live API, so faking a live PASS would violate the Iron Rule. Instead, the harness reports COVERAGE in dry-run and SKIP-with-remediation in live-without-prerequisites.

## Why two harnesses

- **SDK harness** catches API-surface failures (skill activation, hook payload shape, Task tool semantics).
- **Tmux harness** catches CLI-surface failures (slash command routing, terminal output capture, real-user simulation).

Both target the same 5 benchmarks. A real Phase 7 release-candidate run executes both; either one failing blocks release.

## Done condition

✓ Both runners syntax-valid + dry-run exit 0
✓ 5 benchmarks, 5/5 pillar coverage
✓ run-all.sh dry-run exit 0
✓ 0 forbidden file patterns
✓ docs/DEV_HARNESS.md exists
✓ Phase 0+1+2+3+4 regression PASS via doctor.py
