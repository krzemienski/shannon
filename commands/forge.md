---
name: forge
description: Evidence-gated end-to-end completion pipeline. Codebase-analysis → docs-research → planning → oracle plan review → execute → validation → evidence-indexing → reviewer consensus → oracle quorum → completion-gate. Refuses on cited blocker.
replaces:
  - /crucible:forge
argument-hint: "<task> [--mode consensus]"
---

# /shannon:forge

The most rigorous Shannon completion path — engages every gate. Crucible's full pipeline absorbed.

## Inputs

- `<task>` — task description or path to brief
- `--mode consensus` — engages 3-reviewer consensus + 3-auditor oracle quorum

## Behavior (10 phases)

1. **Codebase analysis** — invoke `codebase-analysis` skill. Builds repo-wide context.
2. **Documentation research** — invoke `documentation-research` skill. Fetches current upstream docs for every external dependency.
3. **Planning** — invoke `plan-author` skill with codebase + docs context.
4. **Oracle plan-review** — invoke `oracle-review` skill (pre-execution). 3 auditor agents (critic + reviewer + validator) vote APPROVE/REFUSE in isolated contexts. Quorum: ≥2 APPROVE + 0 unresolved critical blockers. NO execution without approval.
5. **Execute** — dispatch `executor` agent with approved plan.
6. **Validation** — invoke `functional-validation` skill against the executed work.
7. **Evidence indexing** — invoke `evidence-indexing` skill. Every evidence directory gets `README.md` + `INDEX.md`.
8. **Reviewer consensus** — `--mode consensus`: spawn 3 `reviewer` agents independently; each owns an isolated evidence subdir; synthesize via `consensus-engine` skill.
9. **Oracle quorum** — invoke `oracle-review` skill (post-execution). 3 auditor agents audit the evidence package. Quorum required for COMPLETE.
10. **Completion gate** — invoke `completion-gate` skill. Reads `evidence/completion-gate/report.json`. Emits COMPLETE or REFUSED with cited blockers.

## Success criteria

- All 10 phases produced their evidence artifacts.
- Oracle plan-review: APPROVED.
- Functional validation: PASS with citations.
- Reviewer consensus: ≥2/3 PASS (consensus mode).
- Oracle quorum: ≥2/3 APPROVE.
- Completion gate: COMPLETE.

## Hooks fired

- Entire chain. Notable: `evidence-gate-reminder` at every TaskUpdate completion; `block-fab-files` throughout; `validation-not-compilation` after every build.

## Skills invoked

- `codebase-analysis`
- `documentation-research`
- `plan-author`
- `oracle-review` (twice: pre-exec plan review + post-exec evidence audit)
- `functional-validation`
- `evidence-indexing`
- `consensus-engine` (consensus mode only)
- `completion-gate`
- `refusal-discipline` (on any blocker)

## Iron rules

- Refusal is a feature. No `--force` flag.
- Oracle disagreement halts the pipeline.
- Reviewer self-review forbidden (no-self-review).

## Examples

```
/shannon:forge "Add OAuth2 with PKCE to web client"
/shannon:forge plans/260523-feature-x/ --mode consensus
```
