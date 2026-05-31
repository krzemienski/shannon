---
name: consensus-engine
description: Multi-validator agreement gate with 5-state synthesis and multi-round debate iteration. ALWAYS use when the user says "consensus validation", "validate with N reviewers", "agreement gate", "high-confidence validation", "consensus gate", or needs confidence-scored verdicts. Spawns ≥2 (default 3) independent validators in isolated evidence dirs, applies the 5-state synthesis table (UNANIMOUS_PASS / UNANIMOUS_FAIL / MAJORITY_PASS / MAJORITY_FAIL / SPLIT), and escalates SPLIT or borderline MAJORITY to up to 3 rounds of filesystem-mediated debate.
triggers:
  - "consensus validation"
  - "validate with N reviewers"
  - "agreement gate"
  - "high-confidence validation"
  - "consensus gate"
  - "validate with debate"
---

# consensus-engine

Execution-time agreement gate. Spawns ≥2 (default 3) independent validators against the same feature; applies Shannon's 5-state synthesis table; escalates non-unanimous outcomes to multi-round debate via the `judge-with-debate` engine. Synthesizes a confidence-scored verdict.

## 5-state synthesis table (Shannon-distinctive)

| State | Condition | Verdict | Confidence |
|---|---|---|---|
| UNANIMOUS_PASS | All PASS | PASS | HIGH |
| UNANIMOUS_FAIL | All FAIL | FAIL | HIGH |
| MAJORITY_PASS | ≥⅔ PASS (after debate if needed) | PASS | MEDIUM |
| MAJORITY_FAIL | ≥⅔ FAIL (after debate if needed) | FAIL | MEDIUM |
| SPLIT | Neither side ⅔ after max debate rounds | DISAGREEMENT_UNRESOLVED | LOW |

**Confidence never upgrades** — a late-arriving PASS verdict does NOT turn SPLIT into UNANIMOUS_PASS, even if the late verdict is well-evidenced. Confidence is fixed at the time of synthesis.

## Behavior contract

### Phase 1: Setup

1. Dispatch meta-judge ONCE to generate validation rubric YAML (`agents/meta-judge.md`).
2. Create evidence directory structure:
   ```
   e2e-evidence/consensus/<run-id>/
     validator-1/
     validator-2/
     validator-3/
     report.md  (synthesizer-owned)
   ```
3. Store meta-judge YAML at `.shannon/state/consensus-rubric-<run-id>.yaml`.

### Phase 2: Independent validation (parallel)

1. Spawn N consensus-validator subagents in parallel via `Task` (SINGLE assistant response, N Task tool calls). Each receives:
   - The feature / artifact under validation.
   - The meta-judge YAML verbatim.
   - Its assigned validator directory (exclusive write zone).
2. Each validator runs the full journey list independently. **Blind to peer verdicts** in this phase.
3. Each emits a structured YAML verdict header at the START of its report:

```yaml
---
VALIDATOR: {1|2|3}
VERDICT: PASS | FAIL
SCORE: X.X/5.0
CRITERIA:
  - {criterion_1}: {X.X}/5.0
  - {criterion_2}: {X.X}/5.0
ISSUES:
  - {issue with file:line}
EVIDENCE:
  - {evidence_path_1}
  - {evidence_path_2}
---
```

### Phase 3: Initial synthesis

Aggregate verdict headers. Apply 5-state synthesis table:

- Compute `(pass_count, fail_count, total)` per criterion AND overall.
- Map to a state.

If **UNANIMOUS_PASS** or **UNANIMOUS_FAIL** → emit verdict with HIGH confidence; skip Phase 4.

Otherwise → check escalation conditions:
- **SPLIT** (neither side ⅔) → escalate to debate.
- **MAJORITY** with borderline scores (criterion scores disagree by > 1.0 point) → escalate to debate.
- **MAJORITY** with tight agreement (overall scores within 0.5 points) → emit MAJORITY verdict with MEDIUM confidence.

### Phase 4: Multi-round debate (escalation path — engine: `judge-with-debate`)

Delegate to `judge-with-debate` skill for the iteration mechanics. Inputs:
- The N initial validator reports (`.specs/reports/consensus-<run-id>.[1|N].md`).
- The artifact / feature under validation.
- The same meta-judge YAML (no new rubric).

Debate runs up to 3 rounds:

1. Each round: validators read peers' reports DIRECTLY FROM THE FILESYSTEM. Coordinator does NOT relay arguments.
2. Each validator either defends or revises their position, citing the meta-judge YAML rubric as grounding. Arguments must reference specification criteria, NOT opinion.
3. Updates are APPEND-ONLY: each validator appends `## Debate Round R` to their own report file. Previous rounds are preserved.
4. **Convergence thresholds** (Shannon-adopted from sadd):
   - Overall scores within 0.5 points across all validators, AND
   - Every criterion score within 1.0 point across all validators.
5. **Sycophancy detection**: if a validator agrees with another without citing unique evidence, the synthesizer flags the agreement as low-quality and triggers another debate round (up to 3 max).

After convergence (or 3 rounds, whichever first):
- Re-apply 5-state synthesis table to the converged scores.
- If converged to UNANIMOUS → emit with MEDIUM confidence (post-debate UNANIMOUS is not the same as pre-debate UNANIMOUS).
- If converged to MAJORITY → emit MAJORITY verdict with MEDIUM confidence.
- If still SPLIT after 3 rounds → emit SPLIT verdict with LOW confidence; escalate to user with all reports + debate history.

### Phase 5: Per-criterion side-by-side score table

The synthesizer emits a unified report:

```markdown
# Consensus Report — <run-id>

## Per-criterion scores

| Criterion | V1 (initial) | V2 (initial) | V3 (initial) | V1 (final) | V2 (final) | V3 (final) | Consensus | Within Threshold? |
|-----------|-------------|-------------|-------------|-----------|-----------|-----------|-----------|-------------------|
| {criterion_1} | {X.X} | {X.X} | {X.X} | {X.X} | {X.X} | {X.X} | {avg} | YES/NO |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Verdict
- State: {UNANIMOUS_PASS | UNANIMOUS_FAIL | MAJORITY_PASS | MAJORITY_FAIL | SPLIT}
- Final: {PASS | FAIL | DISAGREEMENT_UNRESOLVED}
- Confidence: {HIGH | MEDIUM | LOW}
- Debate Rounds: {0-3}

## Disagreement Protocol Applied (if non-unanimous)
- Diverging criteria: {list}
- Resolution: {converged via debate / re-ran validator / sharpened criterion / discarded erroring validator}

## Cited Evidence
- {file:line} — {context}
- ...
```

## File ownership (LOAD-BEARING)

- **Coordinator**: writes NOTHING.
- **Validator-N**: writes ONLY to `validator-<N>/` subdirectory (append-only across debate rounds).
- **Synthesizer**: writes ONLY `report.md`.
- **Meta-judge**: writes ONLY `.shannon/state/consensus-rubric-<run-id>.yaml`.

A validator that writes outside its directory invalidates the run.

## Disagreement protocol (non-debate fallback)

If debate is not chosen (e.g., user explicitly disables debate), the legacy single-round disagreement protocol still applies:

- Identify diverging criteria.
- Invoke `codebase-analysis` on the divergent evidence.
- Re-resolve via case:
  - (a) re-run missing validator,
  - (b) re-run minority,
  - (c) sharpen criterion (escalate to planner),
  - (d) discard erroring validator.
- If unresolvable → SPLIT with LOW confidence; escalate.

## When to use

- High-stakes change (security, payments, production data).
- Pre-major-release validation.
- After a near-miss bug to harden the gate.
- User explicitly requests `--mode consensus`.

## When NOT to use

- Routine refactor with no behavior change.
- Exploratory work.
- Speed-critical iteration (consensus is 3× the wall time of single-validator).
- Quorum-style plan-review or evidence-audit — use `judge` for those (Shannon-distinctive quorum semantics differ from consensus).

## Iron rules

- **Confidence never upgrades** — a late-arriving PASS does not turn SPLIT into UNANIMOUS.
- **Evidence quality cannot substitute for agreement.** Three highly-evidenced validators in SPLIT remain SPLIT.
- **SPLIT is a real, reportable outcome.** Do NOT silently downgrade to MAJORITY.
- **File ownership is enforced.** Validator-N writes ONLY validator-N/.
- **Filesystem is the debate medium.** Coordinator does NOT relay arguments.
- **Append-only on debate rounds.** Each validator appends `## Debate Round R`; never overwrites.
- **Debate arguments cite the meta-judge YAML rubric**, not opinion.
- **Sycophancy detection** — agreement without unique evidence triggers re-debate.
- **Meta-judge runs ONCE per consensus run; YAML reused across rounds.**
- **Threshold hidden from validators** (delegated via meta-judge YAML).

## Related Skills

- `judge-with-debate` — the iteration engine for Phase 4 escalation.
- `agents/meta-judge.md` — generates the consensus rubric.
- `judge` — alternative quorum gate (pre-execution plan review, post-execution evidence audit); distinct from consensus's "did this feature pass?" semantics.
- `judge` — single-validator primitive used inside each validator.
- `codebase-analysis` — fallback non-debate disagreement protocol.
- `dispatch-parallel` — orchestrates parallel validator spawn.

## Cross-references

- `agents/consensus-validator.md` — the validator agent.
- `agents/meta-judge.md` — rubric generator.
- `core/SUBAGENT_PATTERNS.md` — consensus vs quorum vs debate design rationale.
