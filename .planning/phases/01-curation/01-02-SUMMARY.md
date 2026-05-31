# Summary — Plan 01-02

**Output**: WINNING-scored verdict per skill + `KEEP_PROPOSAL.md` for user approval.

## What landed on disk

- `evidence/winning-scores.md` — 67 rows with W/I/N1/N2/G scores and verdicts
- `evidence/merge-decisions.md` — 7 survivor groups with rationale
- `KEEP_PROPOSAL.md` — the user-facing proposal awaiting approval
- `01-02-VALIDATION.md` — verdict PASS (structural) with out-of-range count flag

## Headline numbers

- KEEP: **41** (above BRIEF target 25-35)
- CUT: 16
- MERGE: 10 absorbing into 7 survivors

## Why KEEP overshoots target

The WINNING filter (W: serves pillar, I: Iron-Rule-aligned, N1: newer source, N2: necessary infra, G: general) is honest about pillar coverage. Most of the inherited 67 skills DO serve at least one pillar (only 22 didn't per 01-01 matrix). Of those 22, only ~6 met the "ruthlessly cut adjacents" rule because most have meaningful WINNING scores via N1 (newer) or N2 (infra-adjacent).

In short: the BRIEF estimate of "25-35" was made before seeing the actual pillar coverage. Either:
- The BRIEF target was too tight (real load-bearing surface is ~40), OR
- The WINNING thresholds need tightening to hit 25-35

The proposal documents this and asks the user to choose.

## Tightening levers if the user wants 25-35

Each of these would cut 6-10 skills:

1. **Cut all `adjacent` role keeps** — would remove ~10 skills (interview-framework, deepen-prompt-plan, commit-work, gepetto, create-meta-prompts, session-handoff, consolidate-memory, deep-interview, preflight, worktree-merge-validate)
2. **Cut all `infra` not strictly required for SDK harness** — would remove ~5 (skill-creator, create-agent-skills, create-slash-commands, mcp-builder, mcp-setup)
3. **More aggressive merges** — collapse all goal-* into one skill (saves 1), collapse all planning skills (plan-author, plan-converge, plan-tournament) into one (saves 2)

My recommendation if the user prioritizes the 25-35 target: combine levers 2 + 3 to land at ~33-35.

## Surprises during the WINNING pass

1. **Iron Rule cluster is dense** — Pillar 3 has 18 skills (anthropic-skills heavily contributed). All 18 are KEEPs by the filter. Hard to cut.
2. **MERGE consolidation worked well** — 10 skills absorbed into 7 survivors (a 30% reduction). Could go further (e.g., merge `judge` into `meta-judge` agent's embedded skills — Architecture C makes this feasible).
3. **No skills were marked REVIEW** — the filter was decisive. If the user wants more deliberation on borderline cases, the REVIEW verdict is available; just none triggered automatically.

## Done condition met

✓ winning-scores.md on disk, 67 rows, valid verdicts
✓ merge-decisions.md documents all MERGE verdicts
✓ KEEP_PROPOSAL.md complete with all sections
✓ Out-of-range condition surfaced to user (not hidden)
✓ Phase 0 + 01-01 regression PASS
✓ Plan 01-03 CORRECTLY blocked on user approval

## What needs user attention

The Open Questions in `KEEP_PROPOSAL.md` (5 questions). The most consequential:
- Question 5: Accept 41 OR tighten to land in 25-35?
- Questions 1-4: specific cluster decisions (prompt-engineering, goal-*, iOS, adjacent-aggressiveness)

User reply form: add a section to `KEEP_PROPOSAL.md` with "USER APPROVED <decisions>" plus any specific adjustments, then Plan 01-03 unblocks.
