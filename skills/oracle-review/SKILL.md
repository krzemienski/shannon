---
name: oracle-review
description: Quorum-gated plan review (pre-execution) AND evidence audit (post-execution) for /shannon:forge. ALWAYS use at forge Phase 4 (plan review) and Phase 9 (evidence audit), or when the user says "oracle review", "plan review", "evidence audit", "quorum review", or "final gate audit". Spawns 3 structurally-independent auditor agents (critic + reviewer + validator) in isolated contexts; requires ≥2 APPROVE and 0 unresolved critical blockers, else invokes refusal-discipline and halts.
triggers:
  - "oracle review"
  - "plan review"
  - "evidence audit"
  - "quorum review"
  - "final gate audit"
---

# oracle-review

Quorum gate. Invoked at two points: BEFORE execution (plan review) AND AFTER execution (evidence audit).

> **Agent mapping note (target adaptation):** Shannon's v1 line absorbed the dedicated `oracle` role into the `critic` / `reviewer` / `validator` triad (see `docs/migration-map.md`). The quorum therefore spawns those three distinct agent types — structural independence satisfies no-self-review (RL-3) without a separate oracle agent. The Phase-8 reviewer *consensus* (3× `reviewer`) and this Phase-9 *quorum* (critic + reviewer + validator) remain separate gates.

## Behavior contract

### Pre-execution (plan-review)

1. Spawn 3 auditor agents in parallel, isolated contexts: `critic`, `reviewer`, `validator`. Each receives the plan + codebase-analysis + documentation-research artifacts.
2. Each independently emits:
   ```
   verdict: APPROVE | REFUSE
   cited_blocker: <if REFUSE, file:line evidence>
   summary: <one paragraph>
   ```
3. Aggregate: ≥2 APPROVE AND 0 unresolved critical blockers → PASS; pipeline proceeds.
4. Otherwise: REFUSE → invoke `refusal-discipline`; halt.

### Post-execution (evidence-audit)

1. Spawn the same 3 auditor agents in parallel, isolated contexts. Each receives the full evidence tree.
2. Each reads cited evidence per MSC, votes APPROVE / REFUSE.
3. Aggregate via the same quorum rule.

## File ownership

- Coordinator: writes nothing.
- Auditor-N: writes ONLY `evidence/oracle-quorum/<run-id>/auditor-<role>/verdict.md`.
- Synthesizer: writes ONLY `evidence/oracle-quorum/<run-id>/report.md`.

## When to use

- Phase 4 of `/shannon:forge` (pre-execution plan review).
- Phase 9 of `/shannon:forge` (post-execution evidence audit).
- Standalone audit via `/shannon:audit`.

## When NOT to use

- Routine `/shannon:cook` runs (lightweight) — only forge invokes the oracle quorum.

## Iron rules

- **Distinct from reviewer consensus.** Quorum = pre-execution plan gate OR final evidence audit (critic+reviewer+validator). Reviewer consensus = post-implementation review (3× reviewer). Both can run for the same forge run.
- **No self-review.** An agent that produced an artifact may not audit it.
- **Quorum is hard.** ≥2/3 APPROVE OR refusal — no `--force`.
- **Citations specific.** Directory references do not count; file path + line range where relevant.
