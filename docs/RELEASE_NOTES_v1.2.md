# Shannon v1.2.0 — Release Notes (Consolidation Edition)

**Date:** 2026-06-02
**Line:** v1.x (supersedes the v1.1 consolidation label; D5 history intact — v1.0.0 tag is truth)

## Summary

v1.2.0 is the **legacy-consolidation maximal-migration edition**. The legacy `shannon-framework/` fork (a 4-era V3→V7 archive) was audited in full and every genuinely-additive, Iron-Rule-legal artifact was migrated into the canonical v1 plugin. Superseded ancestors, a simulated orchestration prototype, a Python test suite, and the dead V5.6 UI were retired with documented cause (`docs/migration-map.md`). DeepPlan is restored as a first-class wave-execution capability.

## Added

- **`/shannon:forge`** — the 10-phase evidence-gated completion pipeline (codebase-analysis → docs-research → planning → oracle plan-review → execute → validation → evidence-indexing → reviewer consensus → oracle quorum → completion-gate). Refuses on any cited blocker; no `--force`. Adapted to the v1 agent set: the oracle quorum spawns `critic + reviewer + validator` (the v1 absorption of the oracle role), keeping no-self-review structural.
- **`documentation-research` skill** — forge Phase 2; fetches + cites current upstream docs (ISO-8601 sourced), refuses memory-only references.
- **`oracle-review` skill** — forge Phase 4 + 9 quorum gate (≥2/3 APPROVE or refuse).
- **`wave-execution` skill** — DeepPlan execution doctrine: dependency-grouped waves, one-message parallel spawn, between-wave synthesis gates. Serena dependency replaced with the on-disk evidence tree + `.shannon/state/` (D3).
- **`deepplan-architect` agent** — deep multi-wave planner; inherits `plan-author, codebase-analysis, skill-inventory, wave-execution`. Drives `/shannon:plan --mode deep`.
- **Activation benchmark harness** (G1) — `scripts/harness/drive-tests.sh` + `drive-tests-csd.sh` prove the opt-in skill-activation gate in **real `claude -p` sessions** (enabled fires / unset+disabled no-op). `benchmarks/innocent-corpus.json` is the precision corpus.
- **Fixtures** (G2) — `fixtures/{enabled,unset,disabled,minimal,complex}` real sample project trees + `.shannon` sentinels (Iron-Rule seed-data, 55/55 ALLOWED).

## Changed

- **Version → 1.2.0** (`plugin.json`, `marketplace.json`).
- **`/shannon:plan --mode deep`** now invokes `deepplan-architect` and a `wave-execution` decomposition step after tournament+converge.
- **`plan-author` skill** — 4 dangling `plan-deepen` cross-refs repointed to `/shannon:plan --mode deep` (the folded mode).
- **`scripts/doctor.py`** — count ranges widened to v1.2 reality (skills 25-40, commands 13-24) reflecting the reversed-D2 additions.
- **`DECISIONS.md`** — D10 appended (consolidation + reversal trail).

## Counts (v1.2.0, doctor-verified)

| Surface | v1.1 | v1.2 |
|---|---|---|
| Commands | 20 | **21** (+forge) |
| Agents | 10 | **11** (+deepplan-architect) |
| Skills | 33 | **36** (+documentation-research, oracle-review, wave-execution) |
| Hooks | 7 | 7 |

`/shannon:doctor` → all checks PASS, 0 mismatches.

## Decisions / reversals (see DECISIONS.md D10)

- **D2 reversed** — the signed component-reduction targets gave way to maximal *value* migration (user call 2026-06-02).
- **APPROVAL-SIGNED.md (2026-06-01) superseded** by a fresh full re-approval at the Phase-3 gate.
- **D5/D6/D7/D8/D9 unchanged.** UI (D7) remains a separate v0.2.0 train.

## Retired-with-reason (Iron Rule honored)

Simulated `orchestration/*.py`, the legacy `pytest` suite (test files forbidden by `block-fab-files`), the dead V5.6 dashboard+server (→ v0.2.0), and the superseded V3-V7 `modules/core/modes` ancestors. Full ledger + rollback steps: `docs/migration-map.md`.

## Evidence

`evidence/legacy-consolidation/forge-fullmig-20260602T005139/` — 15-agent complete-read streams, gap analysis, architecture proposal, signed approval, and validation artifacts (YAML parse, doctor, real-session gate proof).
