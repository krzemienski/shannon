---
name: loop-runner
description: Bounded do-verify-reflect loop with transcript-evidence Iron Rule, stall detection, iteration banner, checklist artifact, and post-iteration cleanup. ALWAYS use when the user says "ralph loop", "iterate until done", "do-verify-reflect", "self-referential loop", "shannon loop", or invokes /shannon:loop. The lower-level loop primitive that autopilot-runner composes for single-phase repetition.
triggers:
  - "ralph loop"
  - "iterate until done"
  - "do-verify-reflect"
  - "self-referential loop"
  - "shannon loop"
  - "bounded iteration"
  - "verify and reflect"
---

# loop-runner

Skill that backs `/shannon:loop`. Bounded do-verify-reflect iteration with the transcript-evidence Iron Rule, stall detection, iteration banner observability, persistent checklist artifact across iterations, and a mandatory post-iteration cleanup pass.

This is the canonical Shannon-native loop primitive. The reference pattern is `ralph` (oh-my-claudecode). Reference disciplines (transcript-evidence, stall, bound-rationale) come from `goal-loop-orchestrator` + `northstar`.

## Behavior contract

### Iteration N (1..max-iter)

1. **Banner** — emit `[SHANNON:LOOP - iter N/M, prior: <fingerprint or "fresh">]` at the top of the iteration. Mirrors `/goal` mid-run observability.
2. **Refine** — if iteration 1 and the success criteria are generic, refine them to be task-specific first (the "CRITICAL: Refine the scaffold" step from ralph). Persist to `e2e-evidence/loop-<run-id>/checklist.json`.
3. **Do** — spawn the executor agent with the iteration-N prompt; capture output to `e2e-evidence/loop-<run-id>/iter-N/`. The executor's last message MUST surface the proving command's stdout/stderr verbatim into the transcript (Iron Rule).
4. **Verify** — invoke `--verify-with` skill (default `functional-validation`). Read its verdict from `e2e-evidence/loop-<run-id>/iter-N/verdict.json`. Apply reviewer tiering (see below).
5. **Iron Rule check** — confirm the verify command's output appears in the transcript of this iteration. If `verdict=PASS` but no transcript proof: rewrite verdict to `REFUSED:iron_rule_no_transcript_proof`.
6. **Reflect** — invoke `reflect` skill against the iteration-N artifact + verdict; produce dominant-gap analysis (≤ 3 gaps) + next-iteration prompt. Update `checklist.json` (flip `passes` flags).
7. **Fingerprint** — append `{iter: N, verdict: <X>, fingerprint: <first 80 chars of first failure>}` to `stall-log.jsonl`.
8. **Stall check** — if the last 3 fingerprints share the same `{verdict, fingerprint}`, exit with `STALLED_SAME_FAILURE`. Do not burn remaining iterations.
9. **Exit condition**:
   - All `checklist.json` entries `passes: true` AND verify PASS AND Iron Rule satisfied → run **cleanup pass** → re-verify → exit `CONVERGED`.
   - N == max-iter and still failing → write `REFUSAL.md`, exit `EXHAUSTED`.
   - Else → increment N, loop.

### Cleanup pass (after success)

After the last iteration reports PASS:
1. Invoke `ai-slop-cleaner` skill on the diff produced by this loop.
2. Re-run the verify skill on the post-cleanup tree.
3. Only the post-cleanup PASS counts as `CONVERGED`. If cleanup re-verify fails, treat as a new iteration and continue.

## Checklist artifact

Persistent across iterations. The single most useful observability artifact.

`e2e-evidence/loop-<run-id>/checklist.json`:
```json
{
  "run_id": "loop-2026-05-27-1430",
  "goal": "make the login flow work end-to-end",
  "max_iter": 8,
  "bound_rationale": "4 features × 2 iterations of refinement",
  "criteria": [
    {"id": "c1", "text": "POST /login returns 200 for valid creds", "passes": true,  "proven_in_iter": 1},
    {"id": "c2", "text": "POST /login returns 401 for invalid creds", "passes": true,  "proven_in_iter": 2},
    {"id": "c3", "text": "session cookie set with Secure+HttpOnly", "passes": false, "proven_in_iter": null}
  ],
  "iterations": [
    {"n": 1, "verdict": "PARTIAL", "fingerprint": "c2 returned 200 not 401"},
    {"n": 2, "verdict": "PARTIAL", "fingerprint": "cookie missing Secure flag"}
  ]
}
```

The loop only converges when every criterion has `passes: true`. The `reflect` step flips flags based on the iteration's verify output.

## Iteration banner

Emit at the start of every iteration (this is what `/shannon:trace` and external observers grep for):

```
[SHANNON:LOOP - iter 3/8, prior: REFUSED:cookie missing Secure flag]
```

Banner format: `[SHANNON:LOOP - iter N/M, prior: <verdict>:<fingerprint or "fresh">]`. One line, plain ASCII. The trailing space after the colon matters for the regex parser.

## Reviewer tiering

Borrowed from ralph (STANDARD vs THOROUGH tier). Applied to the verify skill choice.

- **STANDARD tier** — default. `--verify-with functional-validation`.
- **THOROUGH tier** — auto-elevated when the diff modifies > 20 files OR touches any of: `auth/`, `security/`, `crypto/`, `payments/`, `iam/`. The verify step is run twice: once with `functional-validation`, once with `judge` (or any other strict verify skill). BOTH must PASS for the iteration to be considered PASS.

The tiering decision is logged in `checklist.json` under `tier_chosen` so the audit trail is reproducible.

## Stall detection

Three consecutive iterations with the same `{verdict, fingerprint}` pair → exit `STALLED_SAME_FAILURE`. The fingerprint is the first 80 characters of the first failed criterion's reason from the verify output.

Don't fail on the third occurrence by surprise. Print a warning on the second:

```
[SHANNON:LOOP - WARN] iteration 4 shares fingerprint with iteration 3. One more identical failure will trigger STALLED_SAME_FAILURE.
```

## Bound rationale

When `max-iter` is set, the user (or the calling command) must record a one-line rationale to `checklist.json:bound_rationale`. Example:

- `"max-iter=8, task spans 4 acceptance criteria × ~2 refinement rounds"`

If the loop is invoked without a rationale, the loop-runner writes `bound_rationale: "default; no explicit rationale supplied"` and prints a warning. This is the audit trail that catches runaway loops.

## When to use

- Goal is observable (verify skill exists) but the path isn't.
- Iterative refinement: perf tuning, prompt tuning, layout/UI tuning, flaky-test stabilization.
- Convergent search where each round measurably improves.

## When NOT to use

- Goal not testable as a skill verdict → `/shannon:cook` with explicit plan, or build a verify skill first.
- Time-bounded with a hard wall-clock → max-iter may exhaust silently.
- Multi-actor coordination → `/shannon:team`.
- Whole-app autopilot → `/shannon:autopilot` (use autopilot-runner, which composes this loop per phase).

## Anti-patterns

- Re-running the same iteration with the same prompt — `reflect` MUST produce a different next-prompt each round.
- Skipping the verify step → loop becomes uncontrolled.
- Verifying with a skill that always returns PASS (vague verify) → choose a strict skill, or elevate to THOROUGH tier.
- Trusting an evidence file written by the executor without the proving command appearing in the transcript — Iron Rule violation.
- Treating cleanup as optional. The cleanup pass is part of CONVERGED.

## Iron rules

- **Transcript-evidence**: verify=PASS without the proving command's output in the iteration's transcript is rewritten to REFUSED.
- **One iteration → one evidence dir.** Never reuse iter-N.
- **No override on max-iter.** Refusal exits gracefully via REFUSAL.md.
- **Stall after 3 identical fingerprints.** Don't burn remaining iterations.
- **Cleanup pass is mandatory before CONVERGED.** No "skip cleanup because pressed for time."
- **Checklist updates only via reflect.** The executor cannot flip its own flags.
- **`bound_rationale` is recorded for every run.** Defaulted if not supplied, never absent.

## Cross-references

- `skills/autopilot-runner/SKILL.md` — composes this loop per phase
- `skills/ralph/SKILL.md` — the canonical loop pattern this implementation descends from
- `skills/goal-loop-orchestrator/SKILL.md` — the transcript-evidence discipline source
- `skills/northstar/SKILL.md` — the bound-rationale + adversarial-harden discipline source
- `skills/functional-validation/SKILL.md` — default verify skill
- `skills/judge/SKILL.md` — THOROUGH-tier second verify skill
- `skills/reflect/SKILL.md` — the inner reflection step
- `skills/refusal-discipline/SKILL.md` — REFUSAL.md format on exhaustion


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `ralph`

# ralph

The canonical persistent-loop doctrine. Originated as Geoffrey Huntley's Ralph Wiggum pattern and refined in oh-my-claudecode. Shannon adopts it as the reference doctrine behind `/shannon:loop` (loop-runner) and as a piece every other long-running orchestrator (autopilot, /shannon:cook in long mode) implicitly relies on.

This skill is the **doctrine**; `loop-runner` is the Shannon-native **executor**. They coexist: `ralph` explains the why, `loop-runner` runs the loop.

## The doctrine, in one paragraph

You have a PRD (or any structured set of acceptance criteria with `passes` flags). You loop one iteration at a time. Each iteration picks the next NOT-passing story, executes it, surfaces the proving command's output into the transcript, reviews the result at the right tier, deslops the diff, re-verifies, flips the `passes` flag, appends learnings to `progress.txt`, and continues. You never stop on a transient failure. You exit only on three conditions: every story `passes`, max-iter exhausted, or three iterations in a row with the identical failure fingerprint.

## The five irreducible elements

1. **A `passes`-keyed checklist.** Without this, the loop doesn't know what "done" means. JSON or YAML, persisted across iterations.
2. **A `progress.txt` of learnings.** One line per insight from this run. Carries forward what worked and what didn't.
3. **Iteration banner.** `[RALPH + ULTRAWORK - ITERATION N/M]` (or Shannon's `[SHANNON:LOOP - iter N/M, prior: ...]`). Lets external monitors greppably know where you are.
4. **Post-iteration deslop + regression re-verify.** AI-generated code generates cruft. Without an explicit cleanup pass + re-verify, slop accumulates and the "PASS" verdict drifts.
5. **Stall detection.** If the same failure fingerprint repeats 3 times, escalate. Don't blindly burn iterations.

## The loop, executable

```text
[ITERATION N/M, prior: <fingerprint>]

1. PICK    — open prd.json, pick first story where passes == false
2. PRIME   — load context: progress.txt, the story, related code, related docs
3. REFINE  — if criteria are generic, replace boilerplate with task-specific checks
4. DO      — implement the story; the proving command's stdout MUST appear in transcript
5. REVIEW  — STANDARD or THOROUGH tier reviewer based on file count + risk path
6. DESLOP  — invoke ai-slop-cleaner on the diff
7. RE-VERIFY — run verify again on the post-deslop tree
8. FLIP    — if PASS, prd.json[story].passes = true
9. LEARN   — append one line to progress.txt: "what worked / what didn't"
10. STALL  — append fingerprint to stall-log; if last 3 identical, exit STALLED
```

## Reviewer tiering

- **STANDARD** — diff modifies ≤ 20 files AND touches no high-risk paths. Single verify skill.
- **THOROUGH** — diff modifies > 20 files OR touches `auth/ security/ crypto/ payments/ iam/`. Two verify skills must both PASS (typically `functional-validation` + `judge`).

The tier is recorded in `progress.txt` for the iteration so the audit trail is reproducible.

## The progress.txt protocol

One line per learning. Format:

```
[iter N | YYYY-MM-DDTHH:MM:SSZ] <one-line insight>
```

Examples:
```
[iter 1 | 2026-05-27T14:01:12Z] storing the JWT in localStorage failed CSRF; moved to httpOnly cookie.
[iter 2 | 2026-05-27T14:09:44Z] login flow now passing; rate-limiter blocks valid users at 5 req/min — needs separate iteration.
[iter 3 | 2026-05-27T14:18:01Z] rate-limit window changed to 60s/IP; integration test green.
```

The next iteration reads `progress.txt` FIRST as priming context. This is the durable memory across iterations.

## Mandatory post-iteration deslop

After every PASS-flagged story, before flipping `passes: true`:

1. Run `Skill(ai-slop-cleaner)` against the diff.
2. Run the verify skill again on the post-cleanup tree.
3. Only the post-cleanup PASS counts. If it fails, the story is NOT yet `passes: true`.

The deslop step is the single biggest difference between "the loop says it's done" and "the work is actually done."

## Stall detection

Track fingerprint = `<verdict>:<first 80 chars of first failure reason>`.

After each iteration append to `stall-log.jsonl`. If the last 3 entries share an identical fingerprint, exit `STALLED_SAME_FAILURE`. Write `STALLED.md` listing the fingerprint, the 3 attempts that produced it, and a recommended next manual step.

Warning the user on the **second** occurrence (not just on the third) saves wall-clock:

```
[ralph WARN] iteration 4 shares fingerprint with iteration 3.
One more identical failure will trigger STALLED_SAME_FAILURE.
```

## Banner format

```
[RALPH + ULTRAWORK - ITERATION 3/8]
prior: REFUSED — cookie missing Secure flag
story: c3 — "session cookie set with Secure+HttpOnly"
tier:  STANDARD
```

Shannon's `loop-runner` uses the shorter `[SHANNON:LOOP - iter N/M, prior: ...]`. Both are greppable by `/shannon:trace`.

## When to use

- Any task where you have explicit acceptance criteria and want them all flipped to `passes: true`.
- Refactors with a measurable end state ("0 lint errors", "all tests green", "no `any` types in src/").
- Migration loops (codemods, dependency upgrades) where each touched module is a story.

## When NOT to use

- Ambiguous goal — write the criteria first.
- Single-shot edit — just edit it.
- Human-in-the-loop required between steps — use `/shannon:cook` interactively.

## Anti-patterns

- Skipping the deslop pass. The most common silent regression.
- "Just one more iteration" past `max-iter`. Refuse and write REFUSAL.md.
- Inventing `passes: true` flags. Only the verify skill flips them.
- Treating `progress.txt` as optional. It IS the memory across iterations.
- Letting the same fingerprint slide to a 4th iteration. Stall exit at 3.

## Iron rules

- **The boulder never stops** — but it stops on `STALLED_SAME_FAILURE` and `EXHAUSTED`. "Never stops" is a posture, not a license to spin.
- **The proving command's output appears in the transcript** — every iteration, no exceptions.
- **Deslop + re-verify before flipping `passes`.**
- **`progress.txt` is append-only.** Edits to existing lines = audit-trail forgery.
- **Banner on every iteration.**
- **Reviewer tier is recorded.**

## Cross-references

- `skills/loop-runner/SKILL.md` — Shannon's executor of this doctrine
- `skills/autopilot-runner/SKILL.md` — multi-phase orchestrator that composes ralph loops
- `skills/ai-slop-cleaner/SKILL.md` — the mandatory cleanup pass
- `skills/goal-loop-orchestrator/SKILL.md` — transcript-evidence discipline
- `skills/northstar/SKILL.md` — bound-rationale discipline
- `skills/functional-validation/SKILL.md` — default verify skill
- `skills/judge/SKILL.md` — THOROUGH-tier second verify skill

## Absorbed from `reflect`

# Absorbed content: plan-do-check-act (legacy v7 skill, integrated here)

The Kaizen PDCA cycle for actionable improvement. Backs `/shannon:retro` and `/shannon:why` follow-up.

The v1 design grounds every experiment in **git diff evidence**, applies **dominant-improvement discipline** (one experiment at a time, not batched), enforces an explicit **Do-budget**, adds a **reproducibility re-run**, and integrates the result first-class with `memorize`.

## Behavior contract

### Plan (criterion defined BEFORE Do)

- **Hypothesis** — "Changing X reduces failure rate by Y."
- **Anchor principle** — pick one entry from `references/_plan-do-check-act-improvement-principles.md` (small-batch, fail-fast, reversible-first, etc.) that the hypothesis instantiates. Cite it.
- **Check criterion** — measurable, defined explicitly, defined **before** Do. No "inconclusive" exit option.
- **Experiment scope** — smallest viable test that can yield a verdict.
- **Do budget** — wall-clock OR commit-count limit. If exceeded during Do, experiment fails by definition.

### Do (capture state, bound by budget)

- Implement the experiment on a dedicated branch.
- Capture `git diff <base>..HEAD` verbatim — this is the experiment's diff.
- Capture the criterion-measurement command's full stdout/stderr.
- If Do budget exceeded: stop, mark as FAIL with reason "exceeded Do budget; scope too large to test cheaply."

### Check (measure against pre-declared criterion)

- Run the criterion-measurement command.
- Compare to pre-declared expected signal.
- PASS or FAIL — no "inconclusive."

### Check — reproducibility re-run

- Even on PASS, run the criterion command a **second** time on a clean state (or revert+reapply). If second run doesn't reproduce → downgrade to FAIL with reason "non-reproducible."

### Act (integrate or eliminate, persist via memorize)

- **PASS** → integrate into standard practice:
  - Update relevant rules in CLAUDE.md / project doc.
  - **Invoke `Skill(memorize)`** with type=`feedback`, subtype=`workflow`, body documenting the proven rule.
  - Add a one-line entry to `PDCA-INDEX.md`.
- **FAIL** → eliminate:
  - Revert the experimental diff.
  - **Invoke `Skill(memorize)`** with type=`feedback`, subtype=`expertise`, body noting "this path was tried and disconfirmed, here's why" so future PDCAs don't repeat.
  - Add a one-line entry to `PDCA-INDEX.md`.

## Dominant-improvement discipline

From `lesson-learned`'s "1 + max 2 additional" rule. **At most ONE experiment per PDCA cycle.**

If the retrospective surfaces 5 issues, run 5 PDCAs sequentially — never batch. The single-experiment rule keeps the criterion + diff small enough to be falsifiable.

## Anchor principle catalog

`skills/plan-do-check-act/references/_plan-do-check-act-improvement-principles.md` enumerates the catalog. Examples:

- **Small batch** — change one variable at a time.
- **Fail fast** — design the experiment to disprove quickly.
- **Reversible first** — prefer experiments that can be undone in one commit.
- **Cost of being wrong** — what does the worst case look like?
- **Pareto / 80-20** — does the experiment target the 20% of cases that cause 80% of pain?
- **Convexity** — is the upside larger than the downside if it works?

Every PDCA Plan cites one principle. This grounds the hypothesis in a known pattern.

## Output

`reports/pdca-<slug>.md`:

```markdown
# PDCA: <slug>

## Plan
- **Hypothesis**: <statement>
- **Anchor principle**: <from improvement-principles.md>
- **Check criterion**: <measurable signal>
- **Experiment scope**: <smallest viable>
- **Do budget**: <wall-clock or commit count>

## Do
- **Branch**: <branch-name>
- **Diff** (verbatim from `git diff <base>..HEAD`):
  ```
  <diff>
  ```
- **Time spent**: <actual vs budget>

## Check
- **Command**: `<criterion-measurement command>`
- **First run output** (verbatim):
  ```
  <output>
  ```
- **Reproducibility re-run output** (verbatim):
  ```
  <output>
  ```
- **Verdict**: PASS | FAIL
- **Reason** (if FAIL): <one of: criterion not met, non-reproducible, Do budget exceeded>

## Act
- **Action taken**: <integrated | reverted>
- **Memorize invoked**: yes — slug `<memory-slug>`
- **PDCA-INDEX updated**: yes

## Tone (lesson-learned voice)
<one paragraph in reflective tone: "the experiment shows..." not "you should...">
```

## PDCA-INDEX.md

Aggregate ledger of past experiments. Format:

```markdown
# PDCA index

## 2026-Q2
- [reduce-flake-with-retry](pdca-reduce-flake-with-retry.md) — PASS, integrated as rule "retry once on network calls in tests"
- [shorter-pr-batches](pdca-shorter-pr-batches.md) — FAIL, non-reproducible
- [enforce-mypy-strict](pdca-enforce-mypy-strict.md) — FAIL, Do budget exceeded
```

Parallels `MEMORY.md` as the index of accumulated learnings.

## When to use

- After retrospective identifies a recurring problem (`/shannon:retro` follow-up).
- After root-cause analysis identifies a category-level pattern (`/shannon:why` follow-up).
- When an improvement claim needs validation — not "we should do X" but "X reduces Y by measurable amount."

## When NOT to use

- One-off bug — just fix.
- Already-validated improvement — just adopt.
- Subjective improvement claim ("makes the code feel cleaner") — not falsifiable, not PDCA-shaped.

## Iron rules

- **Criterion defined BEFORE Do.** Non-negotiable.
- **No "results inconclusive."** Define criterion so it cannot be.
- **Failed experiments are wins.** Information has value.
- **One experiment per PDCA.** Never batch.
- **Do budget is mandatory.** Exceeded = FAIL.
- **Reproducibility re-run on PASS.** Single-PASS insufficient.
- **Anchor principle cited.** Every Plan.
- **Memorize invoked on Act.** PASS and FAIL both produce a memory.
- **PDCA-INDEX.md is updated every cycle.**

## Cross-references

- `skills/memorize/SKILL.md` — invoked on Act
- `skills/reflect/SKILL.md` — retrospective discipline source
- `skills/lesson-learned/SKILL.md` — reflective-tone source
- `skills/observability-report/SKILL.md` — surfaces PDCA-INDEX in /shannon:retro
- `skills/why/SKILL.md` (kaizen) — five-whys feeds PDCA hypothesis
- `skills/goal-condition-architect/SKILL.md` — pattern for crafting falsifiable criteria

## References

See `references/_plan-do-check-act-improvement-principles.md` for the principle catalog.
