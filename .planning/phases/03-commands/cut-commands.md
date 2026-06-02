# Phase 3 — Cut / absorbed commands

9 inherited commands removed for v0.1.0. Each has a documented rationale and a pointer to where its semantics moved.

## Absorbed into other commands (8)

| Cut command | Absorbed into | Mechanism |
|---|---|---|
| `dispatch-parallel` | `/shannon:dispatch --mode parallel` | Mode flag; same `Skill: dispatch-parallel` underneath. The parallel-fan-out semantics now ride on the single consolidated entry point. |
| `dispatch-competitive` | `/shannon:dispatch --mode competitive` | Mode flag; engages `Skill: tree-of-thoughts` + `Skill: consensus-engine` + `Task: meta-judge` for ranking. Identical to the legacy command's behavior. |
| `plan-converge` | `/shannon:plan --mode converge` | Mode flag; iterative refine → critique → revise loop with `Task: critic`. Default 3 rounds. |
| `plan-tournament` | `/shannon:plan --mode tournament` | Mode flag; N parallel `Task: planner` candidates from distinct perspectives (security-first / performance-first / simplicity-first). |
| `plan-deep` | `/shannon:plan --mode deep` | Mode flag; runs `--mode tournament` → `--mode converge` → adds validation gates via `Skill: plan-author`. Now also engages `Skill: gepetto` for multi-LLM external review. |
| `audit-completion` | `/shannon:audit --scope completion-evidence` | Scope flag; reads `e2e-evidence/<run-id>/completion-gate/report.json` + spawns `Task: critic` for per-evidence verification. |
| `enable` | `/shannon:enforce on` | Subcommand of the new merged toggle. Same `.shannon/active` sentinel write. |
| `disable` | `/shannon:enforce off` | Subcommand of the new merged toggle. Same `.shannon/disabled` sticky write. |

Rationale for absorption: each merge group was 3-4 commands with overlapping behavior and shared internals. The mode-flag pattern reduces the user-facing surface without losing functionality, and matches the aggressive-merge pattern the user authorized in Phase 1:

> "You're allowed to merge what you're allowed to merge together. So you can order across all of them and something might be repetitive in theory or merge into your mind."

Each consolidated command's body explicitly documents the absorbed modes (see `v1 consolidation:` callout at top of each command file).

## Restored in v1.1 (1) — was: Deferred to v1.x

> **Amendment 2026-06-01 (D6).** `forge` is **restored in v1.1**, reversing the original deferral below. The user signed the reversal (`plans/260601-1712-shannon-consolidation/APPROVAL-SIGNED.md` → G4 / D6): the 10-phase pipeline ships now and gets its own phase. The deferral rationale is retained for the historical trail, but no longer governs — forge is in v1.1. Forge-vs-cook recommended-workflow guidance is documented so the two overlapping pipelines do not confuse users (`cook` = lighter 5-phase path; `forge` = full 10-phase oracle-gated pipeline for high-stakes work).

| Restored command | Original deferral rationale (historical) | Status |
|---|---|---|
| `forge` | The 10-phase Crucible pipeline overlaps substantially with `/shannon:cook` (which is the lighter v0.1.0 path through plan → execute → validate → gate). The two distinguishing features — oracle plan-review pre-execution + oracle quorum post-execution — were absorbed into `/shannon:cook` via the `Task: critic` agent embedded in cook's flow plus the optional `/shannon:audit --scope completion-evidence` for post-hoc oracle-style review. v0.1.0 leaned on `cook` + `audit` + `validate` instead of a separate forge command. | **RESTORED in v1.1 (D6).** No longer deferred — forge ships as a first-class command with its own phase. |

## What this means for cross-references

- Any doc, plan, or memory that mentions a cut command should be updated. Phase 6 (Documentation) will sweep all v1 docs for stale references.
- The `replaces:` lists in v7 frontmatter (which were used to cross-walk legacy plugin commands) are not preserved in v1 frontmatter — v1 is a fresh surface, not a backwards-compatibility layer.

## Verification

- Inherited count: **27** commands (verified via `ls commands/*.md | wc -l` on parent)
- v1 kept: **19** commands (verified via `ls v1/shannon/commands/*.md | wc -l`)
- 27 − 19 = 8 directly cut, BUT v1 adds 1 new (`enforce` merging enable+disable) → net cuts = 9, net absorbed (vs new): 8 absorbed + 1 deferred (forge) + 1 new (enforce, replacing 2). 27 - 9 + 1 = 19 ✓
- Phase 3 gate range: 13-20. Result 19 ✓
