# Gap Taxonomy

> Classification of the gaps a reflect skill surfaces. Naming the gap is half of fixing it.

## Why classify gaps

Reflection that produces "we missed some stuff" is useless. Reflection that produces "we missed a goal-misalignment gap and a verification-discipline gap" is actionable — each gap has a known fix.

The taxonomy here is the catalog of gap types Shannon's reflect skill surfaces. Each has:
- a name
- a definition
- typical symptoms
- the canonical remedy

## The taxonomy

### G-1: Goal-misalignment gap

**Definition:** Work that satisfied the literal task but not the underlying goal.

**Symptoms:**
- "It compiled but doesn't do what I asked."
- "All tests pass but the feature is wrong."
- User asks for the spec to be re-explained when shown the output.

**Cause:** Phase-1 understanding incomplete. The intake didn't surface what "done" actually meant.

**Remedy:** Re-run the interview-framework. Specifically, the "what does done look like" question of Phase 1. Write the intent doc this time.

### G-2: Verification-discipline gap

**Definition:** Claimed PASS without surfaced real-system evidence.

**Symptoms:**
- "Tests pass" verdict without the test runner's actual output in the transcript.
- Build-success claim without the compiler's actual lines.
- File-written claim without `ls -la` of the path.

**Cause:** The gate-validation-discipline was inactive or skipped.

**Remedy:** Tighten the verdict gate. PASS = transcript-surfaced output. No exceptions.

### G-3: Mock-temptation gap

**Definition:** Mock / stub / placeholder introduced during validation work.

**Symptoms:**
- A new `mock_*.py` file in the diff.
- "Stubbed for now, real impl coming" comments.
- Tests that test mocks rather than real interfaces.

**Cause:** The no-mocking-validation-gates was inactive or rationalized around.

**Remedy:** Revert the mock. Find the underlying reason it was tempting (slow dep, missing infra, hard-to-reach state) and fix THAT.

### G-4: Scope-creep gap

**Definition:** Work that ranged beyond what the task asked for.

**Symptoms:**
- Diff includes files unrelated to the stated goal.
- Commits with "while I was here..." messages.
- "I noticed X was wrong too, so I fixed it."

**Cause:** Lack of scope discipline. The intake didn't lock the OUT-of-scope list.

**Remedy:** Revert the scope-creep changes (or move them to a separate PR). Use Phase 1's scope.out list explicitly next time.

### G-5: Scope-undershot gap

**Definition:** Work that stopped short of the stated goal.

**Symptoms:**
- "Partial implementation — finish later" left in code.
- Commits that say "first half" with no second half.
- The stated goal is described in PR text but not actually achieved.

**Cause:** Time/context budget exhausted; the plan didn't break the goal into shippable atomic chunks.

**Remedy:** Identify the unfinished work. Either complete it now or explicitly defer with an issue link.

### G-6: Atomicity gap

**Definition:** Commits / phases that bundle multiple distinct changes.

**Symptoms:**
- "Fix bug + refactor + new feature" in one commit.
- A PR that's actually three unrelated PRs.
- Phase plans with 7+ tasks each.

**Cause:** Plan-author skill didn't enforce 2-3-tasks-per-phase discipline.

**Remedy:** Split commits / phases retroactively if possible. Apply the atomicity rule next time.

### G-7: Communication-debt gap

**Definition:** Significant decisions made without documenting the reasoning.

**Symptoms:**
- "Why is this code this way?" with no traceable answer.
- A pattern in the codebase whose rationale lives only in someone's head.
- Future maintainer has to re-derive what already was decided.

**Cause:** Decisions made in chat or in a meeting; never made it to a written artifact.

**Remedy:** Write a decision record now (ADR-style or a memory). Future questions point there.

### G-8: Validation-skip gap

**Definition:** A phase exit gate was skipped or weakened.

**Symptoms:**
- "Skipping the QA pass — we're confident."
- "Skipping verification — out of context."
- Gate that should have been BLOCKING got marked NICE-TO-HAVE.

**Cause:** Gate-discipline relaxation under time/context pressure. The bias is rationalized as pragmatism.

**Remedy:** Re-impose the gate retroactively. Run the skipped pass NOW. Document why the skip was wrong.

### G-9: Cascade-gap

**Definition:** Reference subfile (`references/foo.md`) was promised but not delivered.

**Symptoms:**
- SKILL.md says "MANDATORY READ references/foo.md" but the file doesn't exist.
- Cascade of progressive-disclosure that breaks at first link.

**Cause:** Migration / rewrite landed the SKILL.md without the supporting cascade subfiles.

**Remedy:** Source the subfile from upstream / write it. If neither feasible, strip the reference from SKILL.md.

### G-10: Re-elicitation gap

**Definition:** The user is being asked something they already answered earlier.

**Symptoms:**
- "What's your scope?" when scope was already given.
- "Which approach?" when an approach was already chosen.
- User: "We talked about this."

**Cause:** Phase 3 (Confirm and Store) was skipped — intent wasn't written to disk, so the next phase re-asked.

**Remedy:** Find the prior answer (chat, file, audit). Write it to disk. Resume without re-asking.

### G-11: Stale-memory gap

**Definition:** Acted on a memory whose underlying fact has since changed.

**Symptoms:**
- "The audit memo says X, but that was 6 months ago."
- A memory file references a function/file that's been renamed/removed.
- Acting on a "current state" memory that's no longer current.

**Cause:** Memory loaded without verification against current state.

**Remedy:** Verify memory against current code/data before acting on it. Update or remove if stale.

### G-12: Context-budget gap

**Definition:** Quality degraded because too much context was consumed before the work finished.

**Symptoms:**
- Final commits in a long session are noticeably worse than early commits.
- Self-lobotomization ("I'll skip this part to save context").
- 80%+ context-window used at task start.

**Cause:** Plan was too large for one session. Atomicity rule violated.

**Remedy:** Stop, write a handoff, resume in a fresh session. Apply tighter atomicity next time.

## Gap-frequency heatmap

Reflecting across many sessions, the most common gaps:

1. G-2 Verification-discipline — pervasive; the gate erosion is a constant tendency
2. G-4 Scope-creep — common when fixing related-but-out-of-scope issues
3. G-7 Communication-debt — chronic; decisions disappear into chat
4. G-12 Context-budget — common with ambitious phases

The least common:
- G-3 Mock-temptation — Shannon hooks catch most attempts
- G-1 Goal-misalignment — when interview-framework runs, this drops to ~0

## Using the taxonomy in reflect runs

The reflect skill's output should:
1. Identify the gap by ID (G-2, G-4, etc.) — not just describe it in prose
2. Cite the specific incident — a commit, a session moment, a file
3. Propose the canonical remedy from this taxonomy
4. Be ≤2 lessons per reflect cycle (dominant-gap discipline — see parent SKILL.md)

```
Reflect output template:

**Gap**: G-2 verification-discipline
**Incident**: 2026-05-27 14:30 — claimed `tests pass` in PR #142 without
  surfaced test output. Transcript: <link>.
**Remedy**: Apply gate-validation-discipline strictly. PASS only with
  surfaced real-system output.
```

## Cross-references

- `skills/reflect/` — parent skill
- `skills/lesson-learned/` — distills reflection into reusable principles
- `skills/gate-validation-discipline/` — addresses G-2 directly
- `skills/no-mocking-validation-gates/` — addresses G-3 directly
- `skills/interview-framework/` — addresses G-1 and G-10
- `skills/plan-author/` — addresses G-4, G-5, G-6, G-12 via atomicity rules
