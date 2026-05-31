# Validation — Plan 01-02

**Plan**: Produce keep/cut/merge proposal with per-skill rationale
**Verdict**: ✅ **PASS** (structural) — but **KEEP count out of BRIEF target range; needs user decision**
**Date**: 2026-05-28

## Gate criteria

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | `evidence/winning-scores.md` has 67 rows, scores 0-5, verdicts in {KEEP, CUT, MERGE, REVIEW} | ✅ PASS | 67 rows, 0 invalid verdicts |
| 2 | `evidence/merge-decisions.md` documents every MERGE verdict | ✅ PASS | 7 survivor entries; all 10 MERGE-verdict skills accounted for |
| 3 | `KEEP_PROPOSAL.md` exists with all required sections | ✅ PASS | Summary + KEEP-by-pillar + CUT + MERGE + Open Questions + Counts + Reversibility |
| 4 | KEEP + CUT + MERGE counts sum to 67 | ✅ PASS | 41 + 16 + 10 = 67 |
| 5 | KEEP count vs BRIEF target documented | ✅ PASS | Proposal Section explicitly states "OUT OF RANGE" with status flag |
| 6 | Phase 0 regression: BRIEF + ROADMAP + DECISIONS + plugin.json still valid | ✅ PASS | All present |
| 7 | 01-01 still PASS | ✅ PASS | 01-01-VALIDATION.md verdict still PASS |

## Final counts

- KEEP: 41 (after merges; includes 7 MERGE survivors)
- CUT: 16
- MERGE: 10 (absorbed into 7 survivors)
- Sum check: 41 + 16 + 10 = 67 ✓

## Status against BRIEF target

| Metric | Value |
|---|---|
| BRIEF target range | 25-35 skills |
| Proposed KEEP | 41 |
| Status | ⚠️ **6 above target** |

## Iron Rule compliance

- Proposal generated from real `evidence/winning-scores.md` (67 rows) — no fabrication
- All KEEP skills exist in `.v7/skill-registry.json` (verified via the source iteration)
- All CUT skills are real skills present in `shannon-framework/skills/` (reversibility preserved)
- All MERGE survivors are actual skills, not invented
- Verification ran against the actual `KEEP_PROPOSAL.md` file on disk

## Why the structural verdict is PASS despite count overshoot

Plan 01-02's gate criterion 5 explicitly states: "KEEP count after merges is documented (whether in target range or not — out-of-range needs explicit note)". The proposal documents the out-of-range condition with status flag and surfaces it in the Open Questions section. The DECISION about how to handle the overshoot is reserved for the user — that's by design.

## Why Plan 01-03 cannot start yet

Plan 01-03 has a hard prerequisite: `KEEP_PROPOSAL.md` must contain "USER APPROVED" or equivalent. The proposal currently shows "⏳ AWAITING APPROVAL". The user has three paths forward:

1. **Accept 41 and revise BRIEF** — relax the BRIEF target to 35-45 (acknowledges that the WINNING filter saw more load-bearing skills than the original budget estimated)
2. **Adjust the proposal** — name specific skills to move from KEEP→CUT (the Open Questions section identifies the candidates)
3. **Run a more aggressive WINNING pass** — re-run 01-02 with tighter scoring thresholds (e.g., require score ≥4 for KEEP; current threshold was 3)

My recommendation: **path 2** — review the Open Questions section, pick which adjacents and historicals to additionally cut, write the answers to `KEEP_PROPOSAL.md`, then approve.

## Done condition

01-02-VALIDATION.md exists (this file). Plan 01-03 BLOCKED on user approval of `KEEP_PROPOSAL.md`.
